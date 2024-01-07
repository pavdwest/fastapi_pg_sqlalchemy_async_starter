use pyo3::prelude::*;
use postgres::{Client, Error, NoTls};
// use std::collections::HashMap;
use std::time::Instant;

struct Book {
    _id: i64,
    _identifier: String,
    _name: String,
    _author: String,
    _release_year: i32,
}

fn instant_to_seconds_elapsed(instant: Instant) -> f64 {
    instant.elapsed().as_millis() as f64 * 0.001
}

fn pg_test(client: &mut Client) -> Result<(), Error> {

    // let mut authors = HashMap::new();
    // authors.insert(String::from("Chinua Achebe"), "Nigeria");
    // authors.insert(String::from("Rabindranath Tagore"), "India");
    // authors.insert(String::from("Anita Nair"), "India");

    // for (key, value) in &authors {
    //     let author = Author {
    //         _id: 0,
    //         name: key.to_string(),
    //         country: value.to_string()
    //     };

    //     client.execute(
    //             "INSERT INTO author (name, country) VALUES ($1, $2)",
    //             &[&author.name, &author.country],
    //     )?;
    // }

    let start = Instant::now();
    let mut books = Vec::new();

    for row in client.query("SELECT id, identifier, name, author, release_year FROM book", &[])? {
        books.push (
            Book {
                _id: row.get(0),
                _identifier: row.get(1),
                _name: row.get(2),
                _author: row.get(3),
                _release_year: row.get(4),
            }
            // println!("Book {} is from {}", book.name, book.author);
        );

    }
    println!(
        "Data load of {} records took {}s ({} records per second.)",
        books.len(),
        instant_to_seconds_elapsed(start),
        books.len() as f64 / instant_to_seconds_elapsed(start),
    );

    let start = Instant::now();
    let mut calc = 0;
    for book in &books {
        calc += book._id;
    }
    println!("Calculation took {}s. Result={}", instant_to_seconds_elapsed(start), calc);
    Ok(())
}

/// Formats the sum of two numbers as string.
#[pyfunction]
fn sum_as_string(a: usize, b: usize) -> PyResult<String> {
    Ok((a + b).to_string())
}

#[pyfunction]
fn pgtc(connection_string: String) -> PyResult<String> {
    // println!("Connection string: {connection_string}");
    let mut client = get_pg_client(&connection_string).unwrap();
    pg_test(&mut client).unwrap();
    Ok("Done".to_string())
}

fn get_pg_client(connection_string: &String) -> Result<Client, Error> {
    Ok(Client::connect(connection_string, NoTls)?)
}

#[pyfunction]
fn fib(n: i64) -> i64 {
    // if n <= 0 {
    //     return 0;
    // } else if n == 1 {
    //     return 1;
    // }   fib(n - 1) + fib(n - 2)

    let (mut a, mut b) = (0, 1);

    for _ in 0..n {
        (a, b) = (b, a + b);
    }

    return a
}

#[pyfunction]
fn is_prime(n: i64) -> i64 {
    if n <= 1 {
        return 0;
    }
    for i in 2..n {
        if n % i == 0 {
            return 0;
        }
    }
    return 1
}

/// A Python module implemented in Rust.
#[pymodule]
fn rst_tax_calculator(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(sum_as_string, m)?)?;
    m.add_function(wrap_pyfunction!(fib, m)?)?;
    m.add_function(wrap_pyfunction!(is_prime, m)?)?;
    m.add_function(wrap_pyfunction!(pgtc, m)?)?;
    Ok(())
}
