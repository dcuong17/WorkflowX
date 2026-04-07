# WorkflowX Backend Reference

> Complete API reference for frontend development.

## Table of Contents

- [System Overview](#system-overview)
- [Authentication](#authentication)
- [API Endpoints](#api-endpoints)
- [Business Logic Rules](#business-logic-rules)

---

## System Overview

**Stack:** Django 6.0 + Django REST Framework 3.16 + MySQL
**Base URL:** `http://localhost:8000/api/v1/`
**API Docs (Swagger):** `http://localhost:8000/api/docs/`

### Data Models

#### User (CustomUser)

| Field      | Type   | Notes               |
|------------|--------|---------------------|
| `id`       | UUID   | Primary key         |
| `email`    | string | Unique, login field |
| `password` | string | Write-only, min 8 chars |

- No `username` field — email is the unique identifier (`USERNAME_FIELD = "email"`)

#### Workspace

| Field             | Type   | Notes                        |
|-------------------|--------|------------------------------|
| `workspace_id`    | UUID   | Primary key                  |
| `workspace_name`  | string | Max 255 chars                |
| `description`     | string | Can be blank                 |
| `created_by`      | UUID   | FK → User (who created it)   |
| `total_tasks`     | int    | Computed (non-deleted tasks) |
| `completed_tasks` | int    | Computed (status = "done")   |
| `created_at`      | datetime | Read-only                |
| `updated_at`      | datetime | Read-only                |

- Soft delete via `is_deleted` flag

#### WorkspaceMember

| Field        | Type   | Notes                        |
|--------------|--------|------------------------------|
| `id`         | UUID   | Primary key                  |
| `workspace`  | UUID   | FK → Workspace               |
| `user`       | UUID   | FK → User                    |
| `role`       | string | `"member"` or `"manager"`    |
| `joined_at`  | datetime | Read-only                |

- `unique_together: (workspace, user)` — a user can only be in a workspace once

#### Task

| Field         | Type       | Notes                                      |
|---------------|------------|--------------------------------------------|
| `id`          | UUID       | Primary key                                |
| `workspace`   | UUID       | FK → Workspace                             |
| `title`       | string     | Max 50 chars                               |
| `description` | string     | Can be blank                               |
| `assign_from` | UUID       | FK → User (creator)                        |
| `assign_to`   | UUID       | FK → User (nullable)                       |
| `status`      | enum       | `"todo"`, `"in_progress"`, `"review"`, `"done"` |
| `deadline`    | datetime   | Nullable, must be in the future             |
| `created_at`  | datetime   | Read-only                                  |
| `updated_at`  | datetime   | Read-only                                  |

- Soft delete via `is_deleted` flag

### Task Status Transitions

```
todo ──────► in_progress ──────► review ──────► done
             ◄─────────         ◄─────────         ◄─────────
```

Allowed transitions:
- `todo` → `in_progress`
- `in_progress` → `todo`, `review`
- `review` → `in_progress`, `done`
- `done` → `review`

---

## Authentication

**Mechanism:** JWT (Simple JWT) — Bearer token authentication.

### Token Lifecycle

1. **Login** → receive `access_token` (expires in 1 day) + `refresh_token` (expires in 7 days)
2. **Every request** → send `access_token` in header
3. **When expired** → refresh using `/api/v1/auth/token/refresh`
4. **Logout** → blacklist the `refresh_token`

### How to Attach Token

```
Authorization: Bearer <access_token>
```

### Auth Endpoints

#### POST `/api/v1/auth/signup`

Create a new user account.

**Body:**
```json
{
  "email": "user@example.com",
  "password": "securepass123"
}
```

**201 Created:**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "message": "Đăng ký thành công!"
}
```

**400 Bad Request:**
```json
{
  "email": ["user with this email already exists."],
  "password": ["Password quá ngắn"]
}
```

**Auth required:** No

---

#### POST `/api/v1/auth/signin`

Login and receive JWT tokens.

**Body:**
```json
{
  "email": "user@example.com",
  "password": "securepass123"
}
```

**200 OK:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

**401 Unauthorized:**
```json
{
  "non_field_errors": ["Sai tên đăng nhập hoặc mật khẩu"]
}
```

**Auth required:** No

---

#### POST `/api/v1/auth/signout`

Blacklist the refresh token.

**Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

**200 OK:**
```json
{
  "message": "Đăng xuất thành công"
}
```

**400 Bad Request:**
```json
{
  "message": "Token không được để trống"
}
```
or
```json
{
  "message": "Token không hợp lệ"
}
```

**Auth required:** No

---

#### POST `/api/v1/auth/token/refresh`

Get a new access token using a refresh token.

**Body:**
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIs..."
}
```

**200 OK:**
```json
{
  "access": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Auth required:** No

---

## API Endpoints

All endpoints below (except auth) require:
```
Authorization: Bearer <access_token>
```

### Workspaces

#### GET `/api/v1/workspace/`

List workspaces the current user is a member of. Excludes deleted workspaces.

**Query params (optional):**
- `workspace_name` — filter by name (DjangoFilterBackend)

**200 OK:**
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "workspace_id": "a1b2c3d4-...",
      "workspace_name": "Project Alpha",
      "description": "Main project workspace",
      "created_by": "550e8400-...",
      "total_tasks": 10,
      "completed_tasks": 3,
      "created_at": "2026-04-01T10:00:00Z",
      "updated_at": "2026-04-05T15:30:00Z"
    }
  ]
}
```

**Auth required:** Yes

Note: Results are paginated (page size: 20).

---

#### POST `/api/v1/workspace/`

Create a new workspace. The creator is automatically added as a "manager".

**Body:**
```json
{
  "workspace_name": "Project Beta",
  "description": "Backend team workspace"
}
```

**201 Created:**
```json
{
  "workspace_id": "b2c3d4e5-...",
  "workspace_name": "Project Beta",
  "description": "Backend team workspace",
  "created_by": "550e8400-...",
  "total_tasks": 0,
  "completed_tasks": 0,
  "created_at": "2026-04-07T10:00:00Z",
  "updated_at": "2026-04-07T10:00:00Z"
}
```

**400 Bad Request:** Validation errors.

**Auth required:** Yes

---

#### GET `/api/v1/workspace/<workspace_id>/`

Get a workspace detail. Only members can access.

**200 OK:**
```json
{
  "workspace_id": "a1b2c3d4-...",
  "workspace_name": "Project Alpha",
  "description": "Main project workspace",
  "created_by": "550e8400-...",
  "total_tasks": 10,
  "completed_tasks": 3,
  "created_at": "2026-04-01T10:00:00Z",
  "updated_at": "2026-04-05T15:30:00Z"
}
```

**403 Forbidden:**
```json
{
  "detail": "Không có quyền truy cập workspace này"
}
```

**404 Not Found:**
```json
{
  "detail": "Không có workspace này"
}
```

**Auth required:** Yes

---

#### PUT `/api/v1/workspace/<workspace_id>/`

Update a workspace. Only managers can edit.

**Body (all fields optional, full replacement):**
```json
{
  "workspace_name": "Updated Name",
  "description": "Updated description"
}
```

**200 OK:** Updated workspace object.

**403 Forbidden:**
```json
{
  "detail": "Chỉ manager mới có quyền chỉnh sửa workspace"
}
```

**Auth required:** Yes

---

#### DELETE `/api/v1/workspace/<workspace_id>/`

Soft-delete a workspace. Only managers can delete.

**204 No Content**

**403 Forbidden:**
```json
{
  "detail": "Chỉ manager mới có quyền xóa workspace"
}
```

**Auth required:** Yes

---

### Workspace Members

#### GET `/api/v1/workspace/<workspace_id>/members/`

List all members of a workspace.

**200 OK:**
```json
[
  {
    "id": "m1m2m3m4-...",
    "workspace": "a1b2c3d4-...",
    "user": "550e8400-...",
    "role": "manager",
    "joined_at": "2026-04-01T10:00:00Z"
  },
  {
    "id": "m5m6m7m8-...",
    "workspace": "a1b2c3d4-...",
    "user": "user-uuid-...",
    "role": "member",
    "joined_at": "2026-04-02T12:00:00Z"
  }
]
```

**Auth required:** Yes

---

#### POST `/api/v1/workspace/<workspace_id>/members/`

Add a new member to the workspace. Always added as `"member"` role regardless of what's sent. Only managers can add.

**Body:**
```json
{
  "user": "user-uuid-..."
}
```
Note: `role` is read-only on the serializer — it is always `"member"` when created.

**201 Created:**
```json
{
  "id": "m9m10m11m-...",
  "workspace": "a1b2c3d4-...",
  "user": "user-uuid-...",
  "role": "member",
  "joined_at": "2026-04-07T10:00:00Z"
}
```

**400 Bad Request:**
```json
{
  "user": ["user with this id already exists."],
  "unique": ["The fields workspace, user must make a unique set."]
}
```

**403 Forbidden:**
```json
{
  "detail": "Chỉ manager mới có quyền thêm thành viên"
}
```

**Auth required:** Yes

---

#### DELETE `/api/v1/workspace/<workspace_id>/members/<pk>/`

Remove a member from the workspace. Only managers can remove.

**204 No Content**

**403 Forbidden:**
```json
{
  "detail": "Chỉ manager mới có quyền xóa thành viên"
}
```

**404 Not Found:**
```json
{
  "detail": "Không tồn tại member này"
}
```

**Auth required:** Yes

---

### Tasks

All task endpoints are nested under workspace:
`/api/v1/workspace/<workspace_id>/tasks/`

#### GET `/api/v1/workspace/<workspace_id>/tasks/`

List all tasks in a workspace (non-deleted).

**200 OK:**
```json
[
  {
    "id": "t1t2t3t4-...",
    "workspace": "a1b2c3d4-...",
    "title": "Implement login",
    "description": "Build JWT auth flow",
    "assign_from": "550e8400-...",
    "assign_to": "user-uuid-...",
    "status": "in_progress",
    "deadline": "2026-04-15T00:00:00Z",
    "created_at": "2026-04-01T10:00:00Z",
    "updated_at": "2026-04-05T15:30:00Z"
  }
]
```

**Auth required:** Yes

---

#### POST `/api/v1/workspace/<workspace_id>/tasks/`

Create a new task. Only managers can create.

**Body:**
```json
{
  "title": "Design database schema",
  "description": "Create models for users, tasks, workspaces...",
  "assign_to": "user-uuid-...",
  "deadline": "2026-04-20T23:59:59Z",
  "status": "todo"
}
```

**201 Created:**
```json
{
  "id": "t5t6t7t8-...",
  "workspace": "a1b2c3d4-...",
  "title": "Design database schema",
  "description": "Create models for users, tasks, workspaces...",
  "assign_from": "550e8400-...",
  "assign_to": "user-uuid-...",
  "status": "todo",
  "deadline": "2026-04-20T23:59:59Z",
  "created_at": "2026-04-07T10:00:00Z",
  "updated_at": "2026-04-07T10:00:00Z"
}
```

**400 Bad Request:**
```json
{
  "title": ["Ensure this field has no more than 50 characters."],
  "assign_to": ["Member không tồn tại trong workspace"],
  "deadline": ["Deadline không được ở quá khứ"]
}
```

**403 Forbidden:**
```json
{
  "detail": "Chỉ manager mới có quyền tạo task"
}
```

**Auth required:** Yes

---

#### GET `/api/v1/workspace/<workspace_id>/tasks/<task_id>/`

Get task detail.

**200 OK:** (same format as task object in list response)

**404 Not Found:**
```json
{
  "detail": "Không tồn tại Task này"
}
```

**Auth required:** Yes

---

#### PUT `/api/v1/workspace/<workspace_id>/tasks/<task_id>/`

Update a task (full replacement). Only managers can edit.

**Body (all writable fields):**
```json
{
  "title": "Updated title",
  "description": "Updated description",
  "assign_to": "user-uuid-...",
  "deadline": "2026-05-01T00:00:00Z",
  "status": "in_progress"
}
```

**200 OK:** Updated task object.

**403 Forbidden:**
```json
{
  "detail": "Chỉ manager mới có quyền chỉnh sửa task"
}
```

**Auth required:** Yes

---

#### DELETE `/api/v1/workspace/<workspace_id>/tasks/<task_id>/`

Soft-delete a task. Only managers can delete.

**204 No Content**

**403 Forbidden:**
```json
{
  "detail": "Chỉ manager mới có quyền xóa task"
}
```

**Auth required:** Yes

---

#### PATCH `/api/v1/workspace/<workspace_id>/tasks/<task_id>/status/`

Update task status with transition validation. Any workspace member (not just managers) can update status.

**Body:**
```json
{
  "status": "in_progress"
}
```

**200 OK:** Updated task object.

**400 Bad Request:**
```json
{
  "error": "Cannot transition from todo to review. Allowed: ['in_progress']"
}
```
or
```json
{
  "error": "Status required"
}
```

**Auth required:** Yes

---

## Business Logic Rules

1. **Workspace ownership** — When a user creates a workspace, they are automatically added as a `"manager"` role member.

2. **Role hierarchy** — Only users with `"manager"` role in a workspace can:
   - Create, update, or delete tasks
   - Add/remove workspace members
   - Update/delete workspace settings
   - `"member"` role users can only: view workspace, list/view tasks, update task status

3. **Task creation requires manager** — Even though a task is conceptually a workspace feature, the `IsWorkspaceManager` permission gate means only managers can create tasks in that workspace.

4. **Status transition is restricted** — Tasks cannot jump statuses arbitrarily. The backend enforces the transition graph (see diagram above). PATCH the dedicated `/status/` endpoint to go through validation.

5. **Task assignee must be a workspace member** — When creating/updating tasks, `assign_to` must be a user that already exists in the workspace. The serializer validates this.

6. **Deadline must be in the future** — The serializer rejects past datetimes. Naive datetimes are auto-converted to UTC.

7. **Soft deletes everywhere** — Workspaces and tasks use an `is_deleted` boolean instead of hard deletes. The `destroy` actions flip the flag. Deleted items are filtered from list/retrieve queries.

8. **Pagination** — List endpoints return paginated results with `count`, `next`, `previous`, `results` keys. Default page size is 20.

9. **JWT lifetime** — Access tokens expire after 1 day. Refresh tokens expire after 7 days. After that, users must log in again.

10. **Title length limit** — Task title has a max length of 50 characters.

## Backend Audit Update (2026-04-07)

The backend was audited and aligned with the required business workflow.

### Implemented changes
- Added a default system role `member` to `CustomUser` and exposed it in signup, signin, and profile responses.
- Preserved profile self-service: users can update their own email and change password, while `role` remains read-only.
- Kept workspace creation self-service and confirmed the creator is automatically inserted into `WorkspaceMember` with role `manager`.
- Enforced that users added later to a workspace are always stored as `member`, even if another role is submitted in the request payload.
- Restricted workspace member listing to authenticated users who already belong to that workspace.
- Reworked task business rules so tasks only move through `in_progress -> in_review -> done` with manager rejection returning `in_review -> in_progress`.
- Removed the old `todo` and `review` workflow from the active task model and added a migration that remaps persisted data: `todo` becomes `in_progress`, `review` becomes `in_review`.
- Prevented task status bypass through the general task update endpoint by making `status` read-only there.
- Enforced that only workspace managers can create, edit, delete, and assign tasks.
- Enforced that a task must be assigned to a workspace `member`; assigning a task to a workspace manager is rejected.
- Enforced that only the assigned member can submit a task from `in_progress` to `in_review`.
- Enforced that only the workspace manager can approve (`in_review -> done`) or reject (`in_review -> in_progress`) a submitted task.
- Added comprehensive pytest coverage in each app `tests.py`, including authentication, workspace role behavior, membership permissions, and the full three-step task review flow.

### Notes
- Any earlier documentation in this file that mentions task statuses `todo` or `review` is obsolete and superseded by the workflow above.
- Any earlier statement saying any workspace member can freely update task status is obsolete; status changes are now restricted by assignee and manager review responsibilities.
