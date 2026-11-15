<!-- extends config/sources/traciora/work/work_item/annotations.md; appended under "## Demo tenant, notes v1" -->

kind task, escalation (a chat handed over to a person) or follow_up (a missed call someone took to call back; origin_ref calls:claim). priority low, normal, high, urgent; urgent is rationed per shop. owner_id empty: nobody owns the card. title_enc and description_enc come back as text but cannot be filtered: filter on plain columns, then read. State group comes from work.work_state.state_group. Closed time, overdue and quiet are read with platform.activity (see RULES).
