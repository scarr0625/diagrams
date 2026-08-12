def cloud_journey_workflow(journey_id):

    analyze_apm(journey_id)

    wait_until_confirmed(journey_id)

    calculate_checklist(journey_id)

    while checklist_not_complete():

        collect_missing_information()

        wait_for_data_change()


    request_governance()

    wait_for_governance_completion()


    request_myaccess_if_required()

    wait_for_myaccess()


    evaluate_readiness()


    generate_app_factory_manifest()


    monitor_provisioning()


    transition_to_bau()