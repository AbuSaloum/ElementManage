from business_logic.generic_operation import GenericOperation
    from business_logic.operations_registry import register_operation

    @register_operation("AA")
    class AaOperation(GenericOperation):
        """
        This operation will look for the environment variable AA_CONFIG_YAML,
        then inside that YAML file, it will find the key 'aa' and read steps_order, steps, etc.

        For example, if AA_CONFIG_YAML=/path/to/aa.yaml,
        it will load that file and expect something like:

            aa:
            record_final_state: true
            ...
            steps_order:
                ...
            steps:
                ...
        """

        def get_operation_name(self) -> str:
            # Tells the GenericOperation to look inside raw_config["aa"] in your YAML
            return "aa"
    