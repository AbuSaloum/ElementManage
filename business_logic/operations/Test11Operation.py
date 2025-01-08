from business_logic.generic_operation import GenericOperation
    from business_logic.operations_registry import register_operation

    @register_operation("TEST11")
    class Test11Operation(GenericOperation):
        """
        This operation will look for the environment variable TEST11_CONFIG_YAML,
        then inside that YAML file, it will find the key 'test11' and read steps_order, steps, etc.

        For example, if TEST11_CONFIG_YAML=/path/to/test11.yaml,
        it will load that file and expect something like:

            test11:
            record_final_state: true
            ...
            steps_order:
                ...
            steps:
                ...
        """

        def get_operation_name(self) -> str:
            # Tells the GenericOperation to look inside raw_config["test11"] in your YAML
            return "test11"
    