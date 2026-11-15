<!-- extends config/sources/traciora/identity/person/annotations.md; appended under "## Demo tenant, notes v1" -->

started_on and ended_on are the employment dates; a person who left keeps every call, shift and punch. To find someone by name, read display_name_enc for the shop's or period's people and match in the result: SQL cannot filter an encrypted column. The same name can belong to the person in the erp source's employee table, which shares no key with this one: match them by name, never by id.
