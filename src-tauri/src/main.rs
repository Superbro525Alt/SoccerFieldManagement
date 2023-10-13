 #![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

 // import serial
 use serialport::prelude::*;
 use std::mem;

 // define COMS

 fn read_serial(ports: std::vec::Vec<String>) {
     for port_name in port_names.iter() {
         let mut port = serialport::new(port_name, 9600)
             .timeout(std::time::Duration::from_millis(10))
             .open()
             .expect("Failed to open port");

         let mut serial_buf: Vec<u8> = vec![0; 100];
         let mut serial_str: String = String::new();

         match port.read(serial_buf.as_mut_slice()) {
             Ok(t) => {
                 serial_str = String::from_utf8_lossy(&serial_buf[..t]).to_string();
             }
             Err(ref e) if e.kind() == std::io::ErrorKind::TimedOut => (),
             Err(e) => eprintln!("{:?}", e),
         }
     }
 }

fn main() {
    tauri::Builder::default()
       .run(tauri::generate_context![read_serial])
       .expect("error while running tauri application");
}