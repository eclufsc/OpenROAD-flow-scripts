#!/usr/bin/env bash
design_dir="./designs"
TIMEOUT=timeout

run_with_timeout() {
    oldopt=$-
    set +e
    $TIMEOUT $@
    ret=$?
    if [[ $ret -eq 124 ]]; then
        ret=0
    fi
    set -$oldopt
    return $ret
}

export QT_DEBUG_PLUGINS=1

while IFS= read -r tech_design; do
    echo "Text read from file: $tech_design"

    : '
    if [ -s logs/"$tech_design"/base/5_2_route.json ]; then
        if [ $(jq -r ".detailedroute__flow__errors__count" logs/"$tech_design"/base/5_2_route.json) -eq 0 ]; then
            if [ ! -s logs/"$tech_design"/base/6_report.json ]; then
                rm logs/"$tech_design"/base/6_report.log
                make DESIGN_CONFIG=./designs/"$tech_design"/config.mk
            fi
        fi
    fi
    '
    
    if [ -s logs/"$tech_design"/epl3/5_2_route.json ]; then
        if [ $(jq -r ".detailedroute__flow__errors__count" logs/"$tech_design"/epl3/5_2_route.json) -eq 0 ]; then
            if [ ! -s logs/"$tech_design"/epl3/6_report.json ]; then
                rm logs/"$tech_design"/epl3/6_report.log
                make DESIGN_CONFIG=./designs/"$tech_design"/config.mk FLOW_VARIANT=epl3 GPL_ROUTABILITY_DRIVEN=0 GPL_TIMING_DRIVEN=0 EPL_PLACE=1
            fi
        fi
    fi

    : '
    if [ -s logs/"$tech_design"/ref/5_2_route.json ]; then
        if [ $(jq -r ".detailedroute__flow__errors__count" logs/"$tech_design"/ref/5_2_route.json) -eq 0 ]; then
            if [ ! -s logs/"$tech_design"/ref/6_report.json ]; then
                rm logs/"$tech_design"/ref/6_report.log
                make DESIGN_CONFIG=./designs/"$tech_design"/config.mk FLOW_VARIANT=ref GPL_ROUTABILITY_DRIVEN=0 GPL_TIMING_DRIVEN=0
            fi
        fi
    fi
    '

    : '
    if [ ! -s logs/"$tech_design"/base/5_2_route.json ]; then
        if [ ! -s logs/"$tech_design"/base/5_1_grt.json ]; then
            run_with_timeout 6h make DESIGN_CONFIG=./designs/"$tech_design"/config.mk place
            run_with_timeout 6h make DESIGN_CONFIG=./designs/"$tech_design"/config.mk cts
            run_with_timeout 6h make DESIGN_CONFIG=./designs/"$tech_design"/config.mk globalroute
            if [ ! -s logs/"$tech_design"/base/5_1_grt.json ]; then
                echo '{"globalroute__flow__errors__count": 1, "timeout": 1}' >> logs/"$tech_design"/base/5_1_grt.json
            fi
        fi
        if [ $(jq -r ".globalroute__flow__errors__count" logs/"$tech_design"/base/5_1_grt.json) -eq 0 ]; then
            echo DESIGN_CONFIG=./designs/"$tech_design"/config.mk
            run_with_timeout 6h make DESIGN_CONFIG=./designs/"$tech_design"/config.mk route
            if [ ! -s logs/"$tech_design"/base/5_2_route.json ]; then
                echo '{"detailedroute__flow__errors__count": 1, "timeout": 1}' >> logs/"$tech_design"/base/5_2_route.json 
            fi
        fi
    fi

    if [ ! -s logs/"$tech_design"/epl2/5_2_route.json ]; then
        if [ ! -s logs/"$tech_design"/epl2/5_1_grt.json ]; then
            run_with_timeout 6h make DESIGN_CONFIG=./designs/"$tech_design"/config.mk FLOW_VARIANT=epl2 GPL_ROUTABILITY_DRIVEN=0 GPL_TIMING_DRIVEN=0 EPL_PLACE=1 place
            run_with_timeout 6h make DESIGN_CONFIG=./designs/"$tech_design"/config.mk FLOW_VARIANT=epl2 GPL_ROUTABILITY_DRIVEN=0 GPL_TIMING_DRIVEN=0 EPL_PLACE=1 cts
            run_with_timeout 6h make DESIGN_CONFIG=./designs/"$tech_design"/config.mk FLOW_VARIANT=epl2 GPL_ROUTABILITY_DRIVEN=0 GPL_TIMING_DRIVEN=0 EPL_PLACE=1 globalroute
            if [ ! -s logs/"$tech_design"/epl2/5_1_grt.json ]; then
                echo '{"globalroute__flow__errors__count": 1, "timeout": 1}' >> logs/"$tech_design"/epl2/5_1_grt.json
            fi
        fi
        if [ $(jq -r ".globalroute__flow__errors__count" logs/"$tech_design"/epl2/5_1_grt.json) -eq 0 ]; then
            echo DESIGN_CONFIG=./designs/"$tech_design"/config.mk FLOW_VARIANT=epl2 EPL_PLACE=1
            run_with_timeout 6h make DESIGN_CONFIG=./designs/"$tech_design"/config.mk FLOW_VARIANT=epl2 GPL_ROUTABILITY_DRIVEN=0 GPL_TIMING_DRIVEN=0 EPL_PLACE=1 route
            if [ ! -s logs/"$tech_design"/epl2/5_2_route.json ]; then
                echo '{"detailedroute__flow__errors__count": 1, "timeout": 1}' >> logs/"$tech_design"/epl2/5_2_route.json 
            fi
        fi
    fi

    if [ ! -s logs/"$tech_design"/ref/5_2_route.json ]; then
        if [ ! -s logs/"$tech_design"/ref/5_1_grt.json ]; then
            run_with_timeout 6h make DESIGN_CONFIG=./designs/"$tech_design"/config.mk FLOW_VARIANT=ref GPL_ROUTABILITY_DRIVEN=0 GPL_TIMING_DRIVEN=0 place
            run_with_timeout 6h make DESIGN_CONFIG=./designs/"$tech_design"/config.mk FLOW_VARIANT=ref GPL_ROUTABILITY_DRIVEN=0 GPL_TIMING_DRIVEN=0 cts
            run_with_timeout 6h make DESIGN_CONFIG=./designs/"$tech_design"/config.mk FLOW_VARIANT=ref GPL_ROUTABILITY_DRIVEN=0 GPL_TIMING_DRIVEN=0 globalroute
            if [ ! -s logs/"$tech_design"/ref/5_1_grt.json ]; then
                echo '{"globalroute__flow__errors__count": 1, "timeout": 1}' >> logs/"$tech_design"/ref/5_1_grt.json
            fi
        fi
        if [ $(jq -r ".globalroute__flow__errors__count" logs/"$tech_design"/ref/5_1_grt.json) -eq 0 ]; then
            echo DESIGN_CONFIG=./designs/"$tech_design"/config.mk FLOW_VARIANT=ref GPL_ROUTABILITY_DRIVEN=0 GPL_TIMING_DRIVEN=0
            run_with_timeout 6h make DESIGN_CONFIG=./designs/"$tech_design"/config.mk FLOW_VARIANT=ref GPL_ROUTABILITY_DRIVEN=0 GPL_TIMING_DRIVEN=0 route
            if [ ! -s logs/"$tech_design"/ref/5_2_route.json ]; then
                echo '{"detailedroute__flow__errors__count": 1, "timeout": 1}' >> logs/"$tech_design"/ref/5_2_route.json
            fi
        fi
    fi
    if [ ! -s logs/"$tech_design"/epl3/5_2_route.json ]; then
        if [ ! -s logs/"$tech_design"/epl3/5_1_grt.json ]; then
            run_with_timeout 6h make DESIGN_CONFIG=./designs/"$tech_design"/config.mk FLOW_VARIANT=epl3 GPL_ROUTABILITY_DRIVEN=0 GPL_TIMING_DRIVEN=0 EPL_PLACE=1 place
            run_with_timeout 6h make DESIGN_CONFIG=./designs/"$tech_design"/config.mk FLOW_VARIANT=epl3 GPL_ROUTABILITY_DRIVEN=0 GPL_TIMING_DRIVEN=0 EPL_PLACE=1 cts
            run_with_timeout 6h make DESIGN_CONFIG=./designs/"$tech_design"/config.mk FLOW_VARIANT=epl3 GPL_ROUTABILITY_DRIVEN=0 GPL_TIMING_DRIVEN=0 EPL_PLACE=1 globalroute
            if [ ! -s logs/"$tech_design"/epl3/5_1_grt.json ]; then
                echo '{"globalroute__flow__errors__count": 1, "timeout": 1}' >> logs/"$tech_design"/epl3/5_1_grt.json
            fi
        fi
        if [ $(jq -r ".globalroute__flow__errors__count" logs/"$tech_design"/epl3/5_1_grt.json) -eq 0 ]; then
            echo DESIGN_CONFIG=./designs/"$tech_design"/config.mk FLOW_VARIANT=epl3 EPL_PLACE=1
            run_with_timeout 6h make DESIGN_CONFIG=./designs/"$tech_design"/config.mk FLOW_VARIANT=epl3 GPL_ROUTABILITY_DRIVEN=0 GPL_TIMING_DRIVEN=0 EPL_PLACE=1 route
            if [ ! -s logs/"$tech_design"/epl3/5_2_route.json ]; then
                echo '{"detailedroute__flow__errors__count": 1, "timeout": 1}' >> logs/"$tech_design"/epl3/5_2_route.json 
            fi
        fi
    fi
    '

done < tests.txt