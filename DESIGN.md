# GNN News App - Design Documentation

## 1. Functional Requirements
- **User Roles**: Reader (follows/likes), Journalist (submits), Editor (approves).
- **Approval Workflow**: Articles are 'Pending' until an Editor approves them.
- **REST API**: Full CRUD support for articles and user engagement.

## 2. Database Schema (ERD)
- **CustomUser**: Extends AbstractUser with roles and subscription M2M fields.
- **Article**: Linked to Publisher (User) and Category. Includes `is_approved` flag.
- **Like/Comment**: Related to Article and User to track engagement.

## 3. UI/UX Plan
- **Mobile First**: Using Bootstrap 5 for a responsive grid.
- **Global Navigation**: Context-aware navbar (shows different links for Editors vs Readers).