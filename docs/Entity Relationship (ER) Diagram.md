Your code implements a complex relational structure. Here is how the tables talk to each other:

Core Relationships:
One-to-Many (1:N):

Category → Article: Articles are organized by topic.

CustomUser (Journalist) → Article: One user can author many stories.

Article → Comment: One story can have a long discussion thread.

Many-to-Many (M:N):

CustomUser ↔ CustomUser: The subscribed_journalists field allows users to follow each other.

Article ↔ CustomUser: The likes field tracks engagement without duplicating data.

Newsletter ↔ CustomUser: Manages mass distribution lists.

Self-Referencing:

The CustomUser model connects back to itself to handle the "Follower/Following" logic for Journalists.