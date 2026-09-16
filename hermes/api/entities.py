from hermes.core.result import Result


def resolve_entity(query: str, entity_type: str | None = None) -> Result:
    if entity_type == 'country':
        return resolve_country(query=query)
    if entity_type == 'company':
        return resolve_company(query=query)


def resolve_country(query: str) -> Result:
    raise NotImplementedError()


def resolve_company(query: str) -> Result:
    raise NotImplementedError()
