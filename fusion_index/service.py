from axiom.scripts.axiomatic import AxiomaticCommand


class FusionIndexConfiguration(AxiomaticCommand):
    """
    Axiomatic subcommand plugin for inspecting and modifying the index service
    configuration.
    """
    name = 'fusion_index'
    description = 'Fusion index service configuration'

__all__ = ['FusionIndexConfiguration']
