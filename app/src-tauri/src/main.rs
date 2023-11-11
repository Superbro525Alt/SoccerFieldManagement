 #![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

 use tauri_plugin_serialport;


fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_serialport::init())
       .run(tauri::generate_context![])
       .expect("error while running tauri application");
}