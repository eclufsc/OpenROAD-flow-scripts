source $::env(SCRIPTS_DIR)/load.tcl
if {
  ![env_var_exists_and_non_empty FLOORPLAN_DEF] &&
  ![env_var_exists_and_non_empty FOOTPRINT] &&
  ![env_var_exists_and_non_empty FOOTPRINT_TCL]
} {
  load_design 2_1_floorplan.odb 2_1_floorplan.sdc
  log_cmd place_pins \
    -hor_layers $::env(IO_PLACER_H) \
    -ver_layers $::env(IO_PLACER_V) \
    -random \
    {*}[env_var_or_empty PLACE_PINS_ARGS]
  write_db $::env(RESULTS_DIR)/2_2_floorplan_io.odb
} else {
  log_cmd exec cp $::env(RESULTS_DIR)/2_1_floorplan.odb $::env(RESULTS_DIR)/2_2_floorplan_io.odb
}