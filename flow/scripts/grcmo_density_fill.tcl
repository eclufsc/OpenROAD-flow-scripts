source $::env(SCRIPTS_DIR)/load.tcl
erase_non_stage_variables final
load_design 5_grcmo.odb 5_grcmo.sdc

if { $::env(USE_FILL) } {
  set_propagated_clock [all_clocks]
  density_fill -rules $::env(FILL_CONFIG)
  # The .v file is just for debugging purposes, not a result of
  # this stage.
  write_verilog $::env(RESULTS_DIR)/6_1_grcmo_fill.v
  write_db $::env(RESULTS_DIR)/6_1_grcmo_fill.odb
} else {
  log_cmd exec cp $::env(RESULTS_DIR)/5_grcmo.odb $::env(RESULTS_DIR)/6_1_grcmo_fill.odb
  # There is no 5_route.v file to copy
}
