source $::env(SCRIPTS_DIR)/load.tcl
erase_non_stage_variables floorplan

if {![env_var_equals IS_CHIP 1]} {
  load_design 2_1_floorplan.odb 2_floorplan.sdc
  log_cmd place_pins \
    -hor_layers $::env(IO_PLACER_H) \
    -ver_layers $::env(IO_PLACER_V) \
    -random \
    {*}[env_var_or_empty PLACE_PINS_ARGS]
  source $::env(SCRIPTS_DIR)/io_placement_util.tcl
  write_db $::env(RESULTS_DIR)/2_2_floorplan_io.odb
} else {
  log_cmd exec cp $::env(RESULTS_DIR)/2_1_floorplan.odb $::env(RESULTS_DIR)/2_2_floorplan_io.odb
}