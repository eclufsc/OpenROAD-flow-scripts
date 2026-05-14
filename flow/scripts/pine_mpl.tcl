source $::env(SCRIPTS_DIR)/load.tcl
erase_non_stage_variables floorplan
load_design 2_2_floorplan_io.odb 2_1_floorplan.sdc

lassign $::env(MACRO_PLACE_HALO) halo_x halo_y

# Run PineMP macro placement
set_pine_mp_halo -halo_x $halo_x -halo_y $halo_y
pine_mp

write_db $::env(RESULTS_DIR)/2_3_floorplan_macro.odb
write_macro_placement $::env(RESULTS_DIR)/2_3_floorplan_macro.tcl