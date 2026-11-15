<!-- extends config/sources/chatwoot/RULES.md; appended under "## Demo tenant, notes v1" -->

## Channels and sessions

- The channel of a chat is its inbox: one inbox per channel, named for it (the web chat, Telegram, and where the tenant runs them VK and Avito). Group by inbox name, never by contact.
- The web chat makes one conversation per visit. A messenger customer keeps one conversation for life: a new message reopens the resolved one. So count customer contacts as **sessions** (the messages between two resolutions), not as conversations, whenever a messenger is in the population. A resolution leaves an activity line (message_type 2) and a row in traciora.resolutions.
- A conversation has no shop. A chat's shop is what the customer said or whose staff member answered it; say which you used.

## Who wrote what

- sender_type AgentBot: the assistant. User: a staff member (sender_id is their Chatwoot user id). Contact: the customer.
- On the web chat the assistant answers first; on the messengers it only prepares drafts, and so does it on any chat a person already owns. A draft is not a message: the words a manager sent after editing a draft are a User message. Draft outcomes (sent as it was, edited, discarded) are not in this database; the Conversations Stats screen counts them.
- A private outgoing message is a staff note. The assistant's hand-over note is a private AgentBot message: it carries the customer's name and phone as the customer gave them, and the chat gets the label handoff until a person replies. A web-chat contact usually holds no phone of its own; the number is in that note.
- The reader cannot see staff names (public.users gives id and type only) or contact details (public.contacts is not readable). To name who answered, say the Chatwoot user id and that the name is on the Conversations screen; to match a customer to the shop system or the calls, take the number from the hand-over note.

## Waits

- First reply in a session: from the session's first customer message to the first public reply after it (traciora.reply_episodes gives every ask and its answer). Say whether the answer was the assistant's or a person's (answered_by_kind).
- A person's first reply: the wait to that person's first public line in the session. On the web chat the first answer is usually the assistant's, so a person's wait starts from the customer message that the assistant handed over, not from the first message of the visit.
- Give medians, in minutes, and say whether you counted clock time or the shop's open time (a chat that arrives at night waits until opening).

## Labels

- Topic labels sit on the conversation as text, public.conversations.cached_label_list (comma-separated). Label definitions and taggings are not readable. handoff is the product's label for a hand-over nobody has answered.
