from enum import StrEnum


class SourceGroup(StrEnum):
    UKRAINE = "ukraine"
    GLOBAL = "global"
    COMPANIES = "companies"
    EVERYWHERE = "everywhere"


UKRAINIAN_SITES = [
    "DOU",
    "DJINNI",
    "HAPPYMONDAY",
    "WORKUA",
]

# Тут мають бути тільки реально перевірені міжнародні джерела
# з packages/models/src/enums/site.enum.ts.
GLOBAL_SITES = [
    # "REMOTEOK",
    # "WEWORKREMOTELY",
    # "REMOTIVE",
]

# Кар’єрні сторінки компаній краще додавати поступово,
# тільки після перевірки, що scraper справді працює.
COMPANY_SITES = [
    # "CANONICAL",
    # "JETBRAINS",
    # "ODOO",
]


SOURCE_GROUPS: dict[SourceGroup, list[str]] = {
    SourceGroup.UKRAINE: UKRAINIAN_SITES,
    SourceGroup.GLOBAL: GLOBAL_SITES,
    SourceGroup.COMPANIES: COMPANY_SITES,
}