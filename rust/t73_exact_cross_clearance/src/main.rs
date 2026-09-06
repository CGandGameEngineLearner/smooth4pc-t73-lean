use flate2::read::GzDecoder;
use num_bigint::BigInt;
use num_rational::BigRational;
use num_traits::{One, ToPrimitive, Zero};
use serde_json::{Value, json};
use std::collections::HashMap;
use std::env;
use std::fs::File;
use std::io::{BufRead, BufReader};
use std::path::Path;
use std::str::FromStr;

type Rat = BigRational;
type Point3 = [Rat; 3];
type Point2 = [Rat; 2];

#[derive(Clone)]
struct StubSegment {
    band: usize,
    piece: String,
    local_segment: usize,
    a: Point3,
    b: Point3,
}

struct ModularStubSegment {
    projected: [[[u64; 2]; 2]; 3],
    approximate: [[f64; 3]; 2],
}

struct RawLift {
    transition: usize,
    band: usize,
    side: String,
    first: [String; 3],
    second: [String; 3],
    endpoint: [String; 3],
}

#[derive(Default)]
struct LineIndex {
    vertical: HashMap<Rat, Vec<usize>>,
    slopes: HashMap<Rat, HashMap<Rat, Vec<usize>>>,
}

#[derive(Clone, Copy)]
enum Projection {
    Xy,
    XyPlusZ,
}

const PRIMES: [u64; 3] = [1_000_000_007, 1_000_000_009, 998_244_353];

fn rat(text: &str) -> Rat {
    if let Some((numerator, denominator)) = text.split_once('/') {
        Rat::new(
            BigInt::from_str(numerator).expect("invalid numerator"),
            BigInt::from_str(denominator).expect("invalid denominator"),
        )
    } else {
        Rat::from_integer(BigInt::from_str(text).expect("invalid integer"))
    }
}

fn point3(value: &Value) -> Point3 {
    let values = value.as_array().expect("point is not an array");
    [
        rat(values[0].as_str().expect("x is not a string")),
        rat(values[1].as_str().expect("y is not a string")),
        rat(values[2].as_str().expect("z is not a string")),
    ]
}

fn raw_point3(value: &Value) -> [String; 3] {
    let values = value.as_array().expect("point is not an array");
    [
        values[0].as_str().expect("x is not a string").to_string(),
        values[1].as_str().expect("y is not a string").to_string(),
        values[2].as_str().expect("z is not a string").to_string(),
    ]
}

fn parse_raw_point3(value: &[String; 3]) -> Point3 {
    [rat(&value[0]), rat(&value[1]), rat(&value[2])]
}

fn project(point: &Point3, projection: Projection) -> Point2 {
    match projection {
        Projection::Xy => [point[0].clone(), point[1].clone()],
        Projection::XyPlusZ => [point[0].clone(), &point[1] + &point[2]],
    }
}

fn gzip_records(path: &Path) -> Vec<Value> {
    let decoder = GzDecoder::new(File::open(path).expect("cannot open gzip input"));
    let mut lines = BufReader::new(decoder).lines();
    lines
        .next()
        .expect("gzip stream has no header")
        .expect("cannot read header");
    lines
        .map(|line| {
            serde_json::from_str(&line.expect("cannot read gzip line"))
                .expect("invalid JSON record")
        })
        .collect()
}

fn load_stub_segments(path: &Path) -> Vec<StubSegment> {
    let mut result = Vec::new();
    for record in gzip_records(path) {
        let band = record["band_index"].as_u64().expect("missing band index") as usize;
        let vertices: Vec<Point3> = record["vertices"]
            .as_array()
            .expect("missing vertices")
            .iter()
            .map(point3)
            .collect();
        for piece in record["piece_ranges"]
            .as_array()
            .expect("missing piece ranges")
        {
            let name = piece["piece"].as_str().expect("missing piece name");
            if !name.contains("stub") && !name.contains("complement") {
                continue;
            }
            let range = piece["segment_range"]
                .as_array()
                .expect("missing segment range");
            let low = range[0].as_u64().expect("bad range") as usize;
            let high = range[1].as_u64().expect("bad range") as usize;
            for index in low..high {
                result.push(StubSegment {
                    band,
                    piece: name.to_string(),
                    local_segment: index - low,
                    a: vertices[index].clone(),
                    b: vertices[index + 1].clone(),
                });
            }
        }
    }
    result
}

fn load_modular_stub_segments(path: &Path) -> Vec<ModularStubSegment> {
    let decoder = GzDecoder::new(File::open(path).expect("cannot open complete core gzip"));
    let mut lines = BufReader::new(decoder).lines();
    lines
        .next()
        .expect("complete core stream has no header")
        .expect("cannot read header");
    let mut result = Vec::new();
    for line in lines {
        let record: Value = serde_json::from_str(&line.expect("cannot read complete core line"))
            .expect("invalid complete core JSON");
        let vertices = record["vertices"].as_array().expect("missing vertices");
        for piece in record["piece_ranges"]
            .as_array()
            .expect("missing piece ranges")
        {
            let name = piece["piece"].as_str().expect("missing piece name");
            if !name.contains("stub") && !name.contains("complement") {
                continue;
            }
            let range = piece["segment_range"]
                .as_array()
                .expect("missing segment range");
            let low = range[0].as_u64().expect("bad range") as usize;
            let high = range[1].as_u64().expect("bad range") as usize;
            for index in low..high {
                let raw_a = raw_point3(&vertices[index]);
                let raw_b = raw_point3(&vertices[index + 1]);
                let a = parse_raw_point3(&raw_a);
                let b = parse_raw_point3(&raw_b);
                let projected = std::array::from_fn(|prime_index| {
                    let prime = PRIMES[prime_index];
                    [
                        projected_mod(&a, Projection::XyPlusZ, prime),
                        projected_mod(&b, Projection::XyPlusZ, prime),
                    ]
                });
                let approximate = [
                    [
                        a[0].to_f64().expect("x does not fit f64"),
                        (&a[1] + &a[2]).to_f64().expect("y+z does not fit f64"),
                        a[2].to_f64().expect("z does not fit f64"),
                    ],
                    [
                        b[0].to_f64().expect("x does not fit f64"),
                        (&b[1] + &b[2]).to_f64().expect("y+z does not fit f64"),
                        b[2].to_f64().expect("z does not fit f64"),
                    ],
                ];
                result.push(ModularStubSegment {
                    projected,
                    approximate,
                });
            }
        }
    }
    result
}

fn build_index(segments: &[StubSegment], projection: Projection) -> LineIndex {
    let mut result = LineIndex::default();
    for (index, segment) in segments.iter().enumerate() {
        let a = project(&segment.a, projection);
        let b = project(&segment.b, projection);
        let dx = &b[0] - &a[0];
        let dy = &b[1] - &a[1];
        if dx.is_zero() {
            result.vertical.entry(a[0].clone()).or_default().push(index);
        } else {
            let slope = dy / dx;
            let intercept = &a[1] - &slope * &a[0];
            result
                .slopes
                .entry(slope)
                .or_default()
                .entry(intercept)
                .or_default()
                .push(index);
        }
    }
    result
}

fn query(index: &LineIndex, point: &Point2) -> Vec<usize> {
    let mut result = index.vertical.get(&point[0]).cloned().unwrap_or_default();
    for (slope, intercepts) in &index.slopes {
        let intercept = &point[1] - slope * &point[0];
        if let Some(values) = intercepts.get(&intercept) {
            result.extend(values.iter().copied());
        }
    }
    result
}

fn pow_mod(mut base: u64, mut exponent: u64, modulus: u64) -> u64 {
    let mut result = 1u64;
    while exponent > 0 {
        if exponent & 1 == 1 {
            result = ((result as u128 * base as u128) % modulus as u128) as u64;
        }
        base = ((base as u128 * base as u128) % modulus as u128) as u64;
        exponent >>= 1;
    }
    result
}

fn bigint_mod(value: &BigInt, modulus: u64) -> u64 {
    let modulus_big = BigInt::from(modulus);
    let remainder = value % &modulus_big;
    let signed = remainder
        .to_i64()
        .expect("modular remainder does not fit i64");
    if signed < 0 {
        (signed + modulus as i64) as u64
    } else {
        signed as u64
    }
}

fn rational_mod(value: &Rat, modulus: u64) -> u64 {
    let numerator = bigint_mod(value.numer(), modulus);
    let denominator = bigint_mod(value.denom(), modulus);
    assert_ne!(denominator, 0, "chosen modular prime divides a denominator");
    ((numerator as u128 * pow_mod(denominator, modulus - 2, modulus) as u128) % modulus as u128)
        as u64
}

fn projected_mod(point: &Point3, projection: Projection, modulus: u64) -> [u64; 2] {
    let x = rational_mod(&point[0], modulus);
    let y = match projection {
        Projection::Xy => rational_mod(&point[1], modulus),
        Projection::XyPlusZ => {
            (rational_mod(&point[1], modulus) + rational_mod(&point[2], modulus)) % modulus
        }
    };
    [x, y]
}

fn modular_collinear(first: [u64; 2], second: [u64; 2], point: [u64; 2], modulus: u64) -> bool {
    let dx = (second[0] + modulus - first[0]) % modulus;
    let dy = (second[1] + modulus - first[1]) % modulus;
    let px = (point[0] + modulus - first[0]) % modulus;
    let py = (point[1] + modulus - first[1]) % modulus;
    let left = (dx as u128 * py as u128) % modulus as u128;
    let right = (dy as u128 * px as u128) % modulus as u128;
    left == right
}

fn parameter_at(segment: &StubSegment, projection: Projection, target: &Point2) -> Option<Rat> {
    let a = project(&segment.a, projection);
    let b = project(&segment.b, projection);
    let dx = &b[0] - &a[0];
    let dy = &b[1] - &a[1];
    let parameter = if !dx.is_zero() {
        (&target[0] - &a[0]) / dx
    } else if !dy.is_zero() {
        (&target[1] - &a[1]) / dy
    } else {
        return None;
    };
    if parameter < Rat::zero() || parameter > Rat::one() {
        return None;
    }
    let reconstructed = [
        &a[0] + &parameter * (&b[0] - &a[0]),
        &a[1] + &parameter * (&b[1] - &a[1]),
    ];
    if &reconstructed == target {
        Some(parameter)
    } else {
        None
    }
}

fn interpolate(segment: &StubSegment, parameter: &Rat) -> Point3 {
    [
        &segment.a[0] + parameter * (&segment.b[0] - &segment.a[0]),
        &segment.a[1] + parameter * (&segment.b[1] - &segment.a[1]),
        &segment.a[2] + parameter * (&segment.b[2] - &segment.a[2]),
    ]
}

fn between(value: &Rat, first: &Rat, second: &Rat) -> bool {
    let low = if first <= second { first } else { second };
    let high = if first <= second { second } else { first };
    low <= value && value <= high
}

fn subtract3(left: &Point3, right: &Point3) -> Point3 {
    [
        &left[0] - &right[0],
        &left[1] - &right[1],
        &left[2] - &right[2],
    ]
}

fn cross3(left: &Point3, right: &Point3) -> Point3 {
    [
        &left[1] * &right[2] - &left[2] * &right[1],
        &left[2] * &right[0] - &left[0] * &right[2],
        &left[0] * &right[1] - &left[1] * &right[0],
    ]
}

fn segments_intersect(first: (&Point3, &Point3), second: (&Point3, &Point3)) -> bool {
    let (a, b) = first;
    let (c, d) = second;
    let u = subtract3(b, a);
    let v = subtract3(d, c);
    let w = subtract3(c, a);
    for (first_axis, second_axis) in [(0usize, 1usize), (0, 2), (1, 2)] {
        let denominator = &u[first_axis] * -&v[second_axis] - &u[second_axis] * -&v[first_axis];
        if !denominator.is_zero() {
            let first_parameter = (&w[first_axis] * -&v[second_axis]
                - &w[second_axis] * -&v[first_axis])
                / &denominator;
            let second_parameter = (&u[first_axis] * &w[second_axis]
                - &u[second_axis] * &w[first_axis])
                / &denominator;
            if first_parameter < Rat::zero()
                || first_parameter > Rat::one()
                || second_parameter < Rat::zero()
                || second_parameter > Rat::one()
            {
                return false;
            }
            return (0..3).all(|axis| {
                &a[axis] + &first_parameter * &u[axis] == &c[axis] + &second_parameter * &v[axis]
            });
        }
    }
    if cross3(&u, &w).iter().any(|value| !value.is_zero()) {
        return false;
    }
    let axis = (0..3)
        .find(|axis| !u[*axis].is_zero())
        .expect("zero first segment");
    let (first_low, first_high) = if a[axis] <= b[axis] {
        (&a[axis], &b[axis])
    } else {
        (&b[axis], &a[axis])
    };
    let (second_low, second_high) = if c[axis] <= d[axis] {
        (&c[axis], &d[axis])
    } else {
        (&d[axis], &c[axis])
    };
    std::cmp::max(first_low, second_low) <= std::cmp::min(first_high, second_high)
}

fn line_candidates(index: &LineIndex, first: &Point3, second: &Point3) -> Vec<usize> {
    let a = project(first, Projection::Xy);
    let b = project(second, Projection::Xy);
    let dx = &b[0] - &a[0];
    let dy = &b[1] - &a[1];
    if dx.is_zero() {
        index.vertical.get(&a[0]).cloned().unwrap_or_default()
    } else {
        let slope = dy / dx;
        let intercept = &a[1] - &slope * &a[0];
        index
            .slopes
            .get(&slope)
            .and_then(|lines| lines.get(&intercept))
            .cloned()
            .unwrap_or_default()
    }
}

fn check_escape_germs(stubs: &[StubSegment], index: &LineIndex, path: &Path) -> Value {
    let records = gzip_records(path);
    if records
        .first()
        .and_then(|record| record["core_vertices"].as_array())
        .map(Vec::len)
        != Some(7)
    {
        return json!({"applicable": false, "escape_germs": 0});
    }
    let mut germs = 0usize;
    let mut candidates = 0usize;
    let mut incidences = 0usize;
    let mut extras = Vec::new();
    for record in records {
        let transition = record["transition_index"]
            .as_u64()
            .expect("missing transition") as usize;
        let band = record["band_index"].as_u64().expect("missing band") as usize;
        let side = record["side"].as_str().expect("missing side");
        let vertices: Vec<Point3> = record["core_vertices"]
            .as_array()
            .expect("missing vertices")
            .iter()
            .map(point3)
            .collect();
        let local = if side == "first" { 0usize } else { 5usize };
        let first = &vertices[local];
        let second = &vertices[local + 1];
        germs += 1;
        for stub_index in line_candidates(index, first, second) {
            candidates += 1;
            let stub = &stubs[stub_index];
            if segments_intersect((first, second), (&stub.a, &stub.b)) {
                if first == &stub.a || first == &stub.b || second == &stub.a || second == &stub.b {
                    incidences += 1;
                } else if extras.len() < 10 {
                    extras.push(json!({
                        "transition": transition,
                        "transition_band": band,
                        "transition_side": side,
                        "stub_band": stub.band,
                        "stub_piece": stub.piece,
                        "stub_segment": stub.local_segment,
                    }));
                }
            }
        }
    }
    json!({
        "applicable": true,
        "escape_germs": germs,
        "exact_collinear_candidates": candidates,
        "expected_endpoint_incidences": incidences,
        "extra_intersections": extras.len(),
        "extra_examples": extras,
    })
}

fn shell_endpoint(first: &Point3, second: &Point3) -> Point3 {
    if first[2] <= second[2] {
        first.clone()
    } else {
        second.clone()
    }
}

fn check_band_columns(stubs: &[StubSegment], index: &LineIndex, path: &Path) -> Value {
    let mut candidates = 0usize;
    let mut incidences = 0usize;
    let mut extras = Vec::new();
    let mut columns = 0usize;
    for record in gzip_records(path) {
        let band = record["band_index"].as_u64().expect("missing band index") as usize;
        for lane_name in [
            "negative_lane_vertices",
            "positive_lane_vertices_reverse_orientation",
        ] {
            let mut vertices: Vec<Point3> = record[lane_name]
                .as_array()
                .expect("missing lane vertices")
                .iter()
                .map(point3)
                .collect();
            if lane_name.starts_with("positive") {
                vertices.reverse();
            }
            for local in [0usize, 4usize] {
                let first = &vertices[local];
                let second = &vertices[local + 1];
                let endpoint = shell_endpoint(first, second);
                let projected = project(&endpoint, Projection::Xy);
                columns += 1;
                for stub_index in query(index, &projected) {
                    candidates += 1;
                    let stub = &stubs[stub_index];
                    if let Some(parameter) = parameter_at(stub, Projection::Xy, &projected) {
                        let intersection = interpolate(stub, &parameter);
                        if between(&intersection[2], &first[2], &second[2]) {
                            if intersection == endpoint {
                                incidences += 1;
                            } else if extras.len() < 10 {
                                extras.push(json!({
                                    "column_band": band,
                                    "column_lane": lane_name,
                                    "column_segment": local,
                                    "stub_band": stub.band,
                                    "stub_piece": stub.piece,
                                    "stub_segment": stub.local_segment,
                                }));
                            }
                        }
                    }
                }
            }
        }
    }
    json!({
        "columns": columns,
        "exact_line_candidates": candidates,
        "expected_endpoint_incidences": incidences,
        "extra_intersections": extras.len(),
        "extra_examples": extras,
    })
}

fn load_target_stub_segments(
    path: &Path,
    targets: &std::collections::HashSet<usize>,
) -> HashMap<usize, StubSegment> {
    let decoder = GzDecoder::new(File::open(path).expect("cannot reopen complete core gzip"));
    let mut lines = BufReader::new(decoder).lines();
    lines
        .next()
        .expect("complete core stream has no header")
        .expect("cannot read header");
    let mut result = HashMap::new();
    let mut global_index = 0usize;
    for line in lines {
        let record: Value = serde_json::from_str(&line.expect("cannot read complete core line"))
            .expect("invalid complete core JSON");
        let band = record["band_index"].as_u64().expect("missing band index") as usize;
        let vertices = record["vertices"].as_array().expect("missing vertices");
        for piece in record["piece_ranges"]
            .as_array()
            .expect("missing piece ranges")
        {
            let name = piece["piece"].as_str().expect("missing piece name");
            if !name.contains("stub") && !name.contains("complement") {
                continue;
            }
            let range = piece["segment_range"]
                .as_array()
                .expect("missing segment range");
            let low = range[0].as_u64().expect("bad range") as usize;
            let high = range[1].as_u64().expect("bad range") as usize;
            for index in low..high {
                if targets.contains(&global_index) {
                    result.insert(
                        global_index,
                        StubSegment {
                            band,
                            piece: name.to_string(),
                            local_segment: index - low,
                            a: point3(&vertices[index]),
                            b: point3(&vertices[index + 1]),
                        },
                    );
                }
                global_index += 1;
            }
        }
    }
    result
}

fn check_transition_lifts(stub_path: &Path, stubs: Vec<ModularStubSegment>, path: &Path) -> Value {
    eprintln!(
        "built modular x,y+z index for {} stub segments",
        stubs.len()
    );
    let mut modular_pairs = 0usize;
    let mut approximate_bounds_survivors = 0usize;
    let mut modular_survivors = 0usize;
    let mut candidates = 0usize;
    let mut incidences = 0usize;
    let mut first_extra: Option<Value> = None;
    let mut lifts = 0usize;
    let mut raw_lifts = Vec::new();
    let mut survivor_pairs = Vec::new();
    for record in gzip_records(path) {
        let transition = record["transition_index"]
            .as_u64()
            .expect("missing transition index") as usize;
        let band = record["band_index"].as_u64().expect("missing band index") as usize;
        let side = record["side"].as_str().expect("missing side");
        let vertices: Vec<Point3> = record["core_vertices"]
            .as_array()
            .expect("missing transition vertices")
            .iter()
            .map(point3)
            .collect();
        let repaired = vertices.len() == 7;
        let local = if side == "first" {
            if repaired { 1usize } else { 0usize }
        } else {
            4usize
        };
        let first = &vertices[local];
        let second = &vertices[local + 1];
        let endpoint = shell_endpoint(first, second);
        lifts += 1;
        let raw_vertices = record["core_vertices"]
            .as_array()
            .expect("missing transition vertices");
        raw_lifts.push(RawLift {
            transition,
            band,
            side: side.to_string(),
            first: raw_point3(&raw_vertices[local]),
            second: raw_point3(&raw_vertices[local + 1]),
            endpoint: if first[2] <= second[2] {
                raw_point3(&raw_vertices[local])
            } else {
                raw_point3(&raw_vertices[local + 1])
            },
        });
        let modular_point: Vec<[u64; 2]> = PRIMES
            .iter()
            .map(|prime| projected_mod(&endpoint, Projection::XyPlusZ, *prime))
            .collect();
        let approximate_point = [
            endpoint[0].to_f64().expect("transition x does not fit f64"),
            (&endpoint[1] + &endpoint[2])
                .to_f64()
                .expect("transition y+z does not fit f64"),
        ];
        let lift_z_low = first[2]
            .to_f64()
            .expect("lift z does not fit f64")
            .min(second[2].to_f64().expect("lift z does not fit f64"));
        let lift_z_high = first[2]
            .to_f64()
            .expect("lift z does not fit f64")
            .max(second[2].to_f64().expect("lift z does not fit f64"));
        for stub_index in 0..stubs.len() {
            modular_pairs += 1;
            let approximate = stubs[stub_index].approximate;
            if (0..2).any(|axis| {
                approximate_point[axis] < approximate[0][axis].min(approximate[1][axis]) - 1e-9
                    || approximate_point[axis]
                        > approximate[0][axis].max(approximate[1][axis]) + 1e-9
            }) {
                continue;
            }
            let dx = approximate[1][0] - approximate[0][0];
            let dk = approximate[1][1] - approximate[0][1];
            let (axis, denominator) = if dx.abs() >= dk.abs() {
                (0usize, dx)
            } else {
                (1usize, dk)
            };
            if denominator.abs() > 1e-15 {
                let parameter = (approximate_point[axis] - approximate[0][axis]) / denominator;
                if !(-1e-9..=1.0 + 1e-9).contains(&parameter) {
                    continue;
                }
                let z = approximate[0][2] + parameter * (approximate[1][2] - approximate[0][2]);
                if z < lift_z_low - 1e-9 || z > lift_z_high + 1e-9 {
                    continue;
                }
            }
            approximate_bounds_survivors += 1;
            if !PRIMES.iter().enumerate().all(|(prime_index, prime)| {
                modular_collinear(
                    stubs[stub_index].projected[prime_index][0],
                    stubs[stub_index].projected[prime_index][1],
                    modular_point[prime_index],
                    *prime,
                )
            }) {
                continue;
            }
            modular_survivors += 1;
            survivor_pairs.push((stub_index, transition));
        }
    }
    drop(stubs);
    eprintln!(
        "modular pass retained {} candidate pairs",
        survivor_pairs.len()
    );
    let target_indices: std::collections::HashSet<usize> =
        survivor_pairs.iter().map(|pair| pair.0).collect();
    let exact_stubs = load_target_stub_segments(stub_path, &target_indices);
    eprintln!("reloaded {} exact stub segments", exact_stubs.len());
    for (stub_index, transition_index) in survivor_pairs {
        candidates += 1;
        let stub = exact_stubs
            .get(&stub_index)
            .expect("missing exact survivor stub");
        let lift = &raw_lifts[transition_index];
        let first = parse_raw_point3(&lift.first);
        let second = parse_raw_point3(&lift.second);
        let endpoint = parse_raw_point3(&lift.endpoint);
        let projected = project(&endpoint, Projection::XyPlusZ);
        if let Some(parameter) = parameter_at(stub, Projection::XyPlusZ, &projected) {
            let intersection = interpolate(stub, &parameter);
            if between(&intersection[2], &first[2], &second[2]) {
                if intersection == endpoint {
                    incidences += 1;
                } else {
                    first_extra = Some(json!({
                        "transition": lift.transition,
                        "transition_band": lift.band,
                        "transition_side": lift.side,
                        "stub_band": stub.band,
                        "stub_piece": stub.piece,
                        "stub_segment": stub.local_segment,
                    }));
                    break;
                }
            }
        }
    }
    json!({
        "shell_lifts": lifts,
        "modular_primes": PRIMES,
        "modular_pairs": modular_pairs,
        "approximate_bounds_survivors": approximate_bounds_survivors,
        "modular_survivors": modular_survivors,
        "exact_line_candidates": candidates,
        "expected_endpoint_incidences": incidences,
        "extra_intersections_at_least": usize::from(first_extra.is_some()),
        "first_extra_intersection": first_extra,
    })
}

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() != 4 {
        eprintln!(
            "usage: t73_exact_cross_clearance COMPLETE_CORE.gz BAND_STRIPS.gz MIDDLE_TRANSITIONS.gz"
        );
        std::process::exit(2);
    }
    let stub_path = Path::new(&args[1]);
    let stubs = load_stub_segments(stub_path);
    let stub_count = stubs.len();
    eprintln!("loaded {} stub segments", stubs.len());
    let xy_index = build_index(&stubs, Projection::Xy);
    eprintln!("built exact xy line index");
    let xy_direction_classes = xy_index.slopes.len() + usize::from(!xy_index.vertical.is_empty());
    let xy_line_keys =
        xy_index.vertical.len() + xy_index.slopes.values().map(HashMap::len).sum::<usize>();
    let band = check_band_columns(&stubs, &xy_index, Path::new(&args[2]));
    eprintln!("finished stub/band column check");
    let escapes = check_escape_germs(&stubs, &xy_index, Path::new(&args[3]));
    eprintln!("finished repaired escape-germ check");
    drop(xy_index);
    drop(stubs);
    eprintln!("released exact xy line index");
    let modular_stubs = load_modular_stub_segments(stub_path);
    let transition = check_transition_lifts(stub_path, modular_stubs, Path::new(&args[3]));
    let passed = band["extra_intersections"].as_u64() == Some(0)
        && (!escapes["applicable"].as_bool().unwrap_or(false)
            || escapes["extra_intersections"].as_u64() == Some(0))
        && transition["extra_intersections_at_least"].as_u64() == Some(0);
    let result = json!({
        "schema": "t73_exact_cross_clearance_rust/v1",
        "stub_segments": stub_count,
        "xy_direction_classes": xy_direction_classes,
        "xy_line_keys": xy_line_keys,
        "stub_band_columns": band,
        "stub_transition_escape_germs": escapes,
        "stub_transition_lifts": transition,
        "verdict": if passed {
            "PASS_EXACT_STUB_CROSS_SYSTEM_CORE_CLEARANCE"
        } else {
            "FAIL_EXACT_STUB_TRANSITION_CROSS_SYSTEM_COLLISION"
        },
    });
    println!(
        "{}",
        serde_json::to_string(&result).expect("cannot encode result")
    );
}
