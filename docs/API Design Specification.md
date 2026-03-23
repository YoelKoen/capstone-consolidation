2. API Design Specification
The evaluator specifically asked for a RESTful API design that allows third-party clients to subscribe to news. You should present this in a table format for clarity.

Method,Endpoint,Data Sent,Purpose
GET,/api/articles/,"Filter: category, publisher",Retrieve all published news stories.
POST,/api/articles/,"title, content, category_id",Journalists submit stories for review.
GET,/api/articles/{id}/,N/A,View full story + total_likes + comments.
PATCH,/api/articles/{id}/,"{""is_approved"": true}",Editor only: Triggers the Publication Signal.
GET,/api/users/profile/,N/A,"View bio, role, and subscribed_journalists."