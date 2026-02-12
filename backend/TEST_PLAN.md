# DreamCanvas Backend Test Plan

## Overview
This document outlines a comprehensive testing strategy for the DreamCanvas backend. The plan covers all components including API endpoints, services, core functionality, models, and background tasks.

## Test Structure

```
backend/tests/
├── conftest.py                  # Shared fixtures and test configuration
├── test_api/
│   ├── __init__.py
│   ├── test_auth.py            # Authentication endpoints
│   ├── test_generation.py      # Image generation endpoints
│   ├── test_gallery.py         # Gallery/listing endpoints
│   ├── test_chat.py            # Chat/prompt enhancement endpoints
│   └── test_websocket.py       # WebSocket connection tests
├── test_services/
│   ├── __init__.py
│   ├── test_user_service.py    # User CRUD operations
│   ├── test_generation_service.py  # Generation workflow
│   ├── test_claude_service.py  # Claude API integration
│   ├── test_image_gen_service.py   # DALL-E/Stability integration
│   └── test_storage_service.py # File storage operations
├── test_core/
│   ├── __init__.py
│   ├── test_security.py        # JWT tokens, password hashing
│   ├── test_middleware.py      # CORS, logging middleware
│   ├── test_dependencies.py    # Dependency injection
│   └── test_exceptions.py      # Error handling
├── test_models/
│   ├── __init__.py
│   ├── test_user_model.py      # User model methods
│   └── test_generation_model.py # Generation model methods
└── test_tasks/
    ├── __init__.py
    ├── test_generation_tasks.py # Celery background tasks
    └── test_cleanup_tasks.py   # Cleanup/maintenance tasks
```

---

## 1. Test Configuration (conftest.py)

### Fixtures to Create:
- **`async_client`** - TestClient for API testing with async support
- **`db_session`** - Test database session with rollback after each test
- **`test_user`** - Create a test user for authenticated endpoints
- **`auth_headers`** - JWT token headers for authentication
- **`mock_redis`** - Mock Redis client for testing cache/pub-sub
- **`mock_celery`** - Mock Celery tasks to test without queue
- **`mock_claude_api`** - Mock Anthropic API responses
- **`mock_dalle_api`** - Mock OpenAI DALL-E API responses
- **`mock_storage`** - Mock storage provider (S3/local)

### Setup:
- Database: Use in-memory SQLite or test PostgreSQL database
- Isolation: Each test runs in a transaction that's rolled back
- Async support: Configure pytest-asyncio
- Environment: Override settings for test mode

---

## 2. API Endpoint Tests (test_api/)

### 2.1 Authentication Tests (test_auth.py)

#### Test Cases:

**POST /api/v1/auth/register**
- ✅ `test_register_success` - Create new user with valid data
- ✅ `test_register_duplicate_email` - Reject duplicate email (400)
- ✅ `test_register_invalid_email` - Reject malformed email (422)
- ✅ `test_register_weak_password` - Reject weak password (422)
- ✅ `test_register_missing_fields` - Reject incomplete data (422)
- ✅ `test_register_returns_tokens` - Verify JWT tokens are returned

**POST /api/v1/auth/login**
- ✅ `test_login_success` - Login with valid credentials
- ✅ `test_login_invalid_email` - Reject unknown email (401)
- ✅ `test_login_invalid_password` - Reject wrong password (401)
- ✅ `test_login_inactive_user` - Reject deactivated account (401)
- ✅ `test_login_returns_user_info` - Verify user data in response

**POST /api/v1/auth/refresh**
- ✅ `test_refresh_token_success` - Get new access token with valid refresh token
- ✅ `test_refresh_token_invalid` - Reject invalid refresh token (401)
- ✅ `test_refresh_token_expired` - Reject expired refresh token (401)
- ✅ `test_refresh_token_wrong_type` - Reject access token as refresh token (401)
- ✅ `test_refresh_token_rotation` - Verify new refresh token is issued

**GET /api/v1/auth/me**
- ✅ `test_get_current_user_success` - Get authenticated user profile
- ✅ `test_get_current_user_no_auth` - Reject unauthenticated request (401)
- ✅ `test_get_current_user_invalid_token` - Reject invalid token (401)
- ✅ `test_get_current_user_expired_token` - Reject expired token (401)

**PATCH /api/v1/auth/me**
- ✅ `test_update_profile_success` - Update user profile fields
- ✅ `test_update_display_name` - Update display name only
- ✅ `test_update_bio` - Update bio only
- ✅ `test_update_avatar_url` - Update avatar URL
- ✅ `test_update_preferences` - Merge preferences (not replace)
- ✅ `test_update_profile_no_auth` - Reject unauthenticated (401)
- ✅ `test_update_profile_validation` - Validate field constraints

---

### 2.2 Generation Tests (test_generation.py)

#### Test Cases:

**POST /api/v1/generate**
- ✅ `test_create_generation_async_success` - Create generation (async mode)
- ✅ `test_create_generation_sync_success` - Create generation (sync mode)
- ✅ `test_create_generation_with_style` - Apply style preset
- ✅ `test_create_generation_with_size` - Specify image size
- ✅ `test_create_generation_with_quality` - Specify quality (hd/standard)
- ✅ `test_create_generation_provider_dalle` - Use DALL-E provider
- ✅ `test_create_generation_provider_stability` - Use Stability provider
- ✅ `test_create_generation_enhance_prompt_true` - Enable prompt enhancement
- ✅ `test_create_generation_enhance_prompt_false` - Disable prompt enhancement
- ✅ `test_create_generation_rate_limit` - Enforce rate limit (429)
- ✅ `test_create_generation_no_auth` - Reject unauthenticated (401)
- ✅ `test_create_generation_empty_prompt` - Reject empty prompt (422)
- ✅ `test_create_generation_prompt_too_long` - Reject prompt > 4000 chars (422)

**GET /api/v1/generate/{id}**
- ✅ `test_get_generation_success` - Get generation by ID
- ✅ `test_get_generation_not_found` - Return 404 for unknown ID
- ✅ `test_get_generation_wrong_user` - Reject access to other user's generation (404)
- ✅ `test_get_generation_no_auth` - Reject unauthenticated (401)
- ✅ `test_get_generation_all_statuses` - Verify response for each status

**GET /api/v1/generate/{id}/status**
- ✅ `test_get_generation_status_pending` - Status for pending generation
- ✅ `test_get_generation_status_processing` - Status for processing
- ✅ `test_get_generation_status_completed` - Status with image URLs
- ✅ `test_get_generation_status_failed` - Status with error message
- ✅ `test_get_generation_status_not_found` - Return 404 for unknown ID

**DELETE /api/v1/generate/{id}**
- ✅ `test_delete_generation_success` - Delete own generation
- ✅ `test_delete_generation_cancels_task` - Cancel running Celery task
- ✅ `test_delete_generation_removes_file` - Delete from storage
- ✅ `test_delete_generation_not_found` - Return 404 for unknown ID
- ✅ `test_delete_generation_wrong_user` - Reject deletion of other user's gen (404)
- ✅ `test_delete_generation_no_auth` - Reject unauthenticated (401)

---

### 2.3 Gallery Tests (test_gallery.py)

#### Test Cases:

**GET /api/v1/gallery**
- ✅ `test_list_generations_success` - Get paginated list of generations
- ✅ `test_list_generations_pagination` - Verify page/page_size work
- ✅ `test_list_generations_filter_by_status` - Filter by status
- ✅ `test_list_generations_filter_completed` - Show only completed
- ✅ `test_list_generations_filter_failed` - Show only failed
- ✅ `test_list_generations_empty` - Handle empty result set
- ✅ `test_list_generations_ordering` - Verify newest first ordering
- ✅ `test_list_generations_no_auth` - Reject unauthenticated (401)
- ✅ `test_list_generations_only_own` - Don't show other users' generations
- ✅ `test_list_generations_total_count` - Verify total count accuracy
- ✅ `test_list_generations_page_limit` - Verify page_size max (100)

---

### 2.4 Chat Tests (test_chat.py)

#### Test Cases:

**POST /api/v1/chat**
- ✅ `test_chat_success` - Chat with Claude for prompt help
- ✅ `test_chat_with_history` - Continue conversation with history
- ✅ `test_chat_suggested_prompt` - Extract suggested prompt from response
- ✅ `test_chat_no_auth` - Reject unauthenticated (401)
- ✅ `test_chat_empty_message` - Reject empty message (422)
- ✅ `test_chat_claude_unavailable` - Graceful degradation when Claude unavailable (503)
- ✅ `test_chat_rate_limit` - Handle Claude rate limit error

**POST /api/v1/chat/enhance**
- ✅ `test_enhance_prompt_success` - Enhance a prompt
- ✅ `test_enhance_prompt_with_style` - Apply style parameter
- ✅ `test_enhance_prompt_with_negative` - Apply negative prompt
- ✅ `test_enhance_prompt_style_suggestions` - Return style suggestions
- ✅ `test_enhance_prompt_no_auth` - Reject unauthenticated (401)
- ✅ `test_enhance_prompt_empty` - Reject empty prompt (422)
- ✅ `test_enhance_prompt_claude_unavailable` - Return original when unavailable

---

### 2.5 WebSocket Tests (test_websocket.py)

#### Test Cases:

**WS /api/v1/ws/generations**
- ✅ `test_websocket_connect_success` - Connect with valid token
- ✅ `test_websocket_connect_invalid_token` - Reject invalid token
- ✅ `test_websocket_connect_no_token` - Reject missing token
- ✅ `test_websocket_connect_expired_token` - Reject expired token
- ✅ `test_websocket_welcome_message` - Receive welcome message on connect
- ✅ `test_websocket_subscribe_generation` - Subscribe to generation updates
- ✅ `test_websocket_unsubscribe_generation` - Unsubscribe from updates
- ✅ `test_websocket_receive_updates` - Receive status updates
- ✅ `test_websocket_ping_pong` - Ping/pong heartbeat
- ✅ `test_websocket_heartbeat` - Auto heartbeat on timeout
- ✅ `test_websocket_unknown_action` - Handle unknown action gracefully
- ✅ `test_websocket_max_connections` - Enforce connection limit per user
- ✅ `test_websocket_disconnect_cleanup` - Clean up on disconnect

---

## 3. Service Layer Tests (test_services/)

### 3.1 User Service Tests (test_user_service.py)

#### Test Cases:

**UserService.create()**
- ✅ `test_create_user_success` - Create new user
- ✅ `test_create_user_duplicate_email` - Reject duplicate email
- ✅ `test_create_user_password_hashed` - Verify password is hashed
- ✅ `test_create_user_email_lowercase` - Store email in lowercase
- ✅ `test_create_user_defaults` - Verify default values (is_active=True)

**UserService.get_by_id()**
- ✅ `test_get_user_by_id_success` - Get user by UUID
- ✅ `test_get_user_by_id_string` - Accept UUID as string
- ✅ `test_get_user_by_id_not_found` - Return None for unknown ID
- ✅ `test_get_user_by_id_invalid_uuid` - Handle invalid UUID string

**UserService.get_by_email()**
- ✅ `test_get_user_by_email_success` - Get user by email
- ✅ `test_get_user_by_email_case_insensitive` - Case-insensitive lookup
- ✅ `test_get_user_by_email_not_found` - Return None for unknown email

**UserService.authenticate()**
- ✅ `test_authenticate_success` - Authenticate valid credentials
- ✅ `test_authenticate_invalid_email` - Return None for unknown email
- ✅ `test_authenticate_invalid_password` - Return None for wrong password
- ✅ `test_authenticate_inactive_user` - Return None for inactive user

**UserService.update()**
- ✅ `test_update_user_display_name` - Update display name
- ✅ `test_update_user_bio` - Update bio
- ✅ `test_update_user_avatar` - Update avatar URL
- ✅ `test_update_user_preferences` - Update preferences

**UserService.update_password()**
- ✅ `test_update_password_success` - Change password
- ✅ `test_update_password_wrong_current` - Reject wrong current password
- ✅ `test_update_password_hashed` - Verify new password is hashed

**UserService.deactivate() / activate()**
- ✅ `test_deactivate_user` - Deactivate user account
- ✅ `test_activate_user` - Reactivate user account

---

### 3.2 Generation Service Tests (test_generation_service.py)

#### Test Cases:

**GenerationService.create_generation()**
- ✅ `test_create_generation_success` - Create generation record
- ✅ `test_create_generation_defaults` - Verify default provider/model
- ✅ `test_create_generation_custom_provider` - Use specified provider
- ✅ `test_create_generation_status_pending` - Initial status is pending

**GenerationService.process_generation()**
- ✅ `test_process_generation_full_workflow` - Complete workflow (enhance → generate → upload)
- ✅ `test_process_generation_without_enhancement` - Skip Claude enhancement
- ✅ `test_process_generation_dalle_success` - DALL-E generation
- ✅ `test_process_generation_stability_success` - Stability generation
- ✅ `test_process_generation_image_url` - Upload from URL
- ✅ `test_process_generation_image_data` - Upload from bytes
- ✅ `test_process_generation_stores_metadata` - Store generation metadata
- ✅ `test_process_generation_updates_user_count` - Increment user generation count
- ✅ `test_process_generation_enhancement_failure` - Handle Claude failure gracefully
- ✅ `test_process_generation_generation_failure` - Handle DALL-E failure
- ✅ `test_process_generation_upload_failure` - Handle storage failure
- ✅ `test_process_generation_marks_failed` - Mark as failed on error

**GenerationService.get_generation()**
- ✅ `test_get_generation_by_id` - Get generation by ID
- ✅ `test_get_generation_with_user_filter` - Filter by user_id
- ✅ `test_get_generation_not_found` - Return None for unknown ID

**GenerationService.list_generations()**
- ✅ `test_list_generations_pagination` - Paginate results
- ✅ `test_list_generations_filter_status` - Filter by status
- ✅ `test_list_generations_ordering` - Order by created_at desc
- ✅ `test_list_generations_count` - Return accurate total count

**GenerationService.delete_generation()**
- ✅ `test_delete_generation_success` - Delete generation
- ✅ `test_delete_generation_removes_from_storage` - Delete from storage
- ✅ `test_delete_generation_removes_from_db` - Delete from database

**GenerationService.check_rate_limit()**
- ✅ `test_check_rate_limit_allowed` - Allow under limit
- ✅ `test_check_rate_limit_exceeded` - Block when limit exceeded
- ✅ `test_check_rate_limit_hourly_window` - Verify 1-hour sliding window

---

### 3.3 Claude Service Tests (test_claude_service.py)

#### Test Cases:

**ClaudeService.is_available**
- ✅ `test_is_available_with_api_key` - Return True when configured
- ✅ `test_is_available_without_api_key` - Return False when not configured

**ClaudeService.enhance_prompt()**
- ✅ `test_enhance_prompt_success` - Enhance a prompt
- ✅ `test_enhance_prompt_with_style` - Apply style parameter
- ✅ `test_enhance_prompt_with_negative` - Apply negative prompt
- ✅ `test_enhance_prompt_returns_suggestions` - Return style suggestions
- ✅ `test_enhance_prompt_json_parse_success` - Parse JSON response
- ✅ `test_enhance_prompt_json_parse_failure` - Handle non-JSON response
- ✅ `test_enhance_prompt_unavailable` - Return original when unavailable
- ✅ `test_enhance_prompt_rate_limit` - Handle rate limit error
- ✅ `test_enhance_prompt_connection_error` - Handle connection error
- ✅ `test_enhance_prompt_api_error` - Handle API error

**ClaudeService.chat()**
- ✅ `test_chat_success` - Chat with Claude
- ✅ `test_chat_with_history` - Include conversation history
- ✅ `test_chat_extracts_suggested_prompt` - Extract "SUGGESTED PROMPT:"
- ✅ `test_chat_unavailable` - Return error message when unavailable
- ✅ `test_chat_rate_limit` - Handle rate limit gracefully
- ✅ `test_chat_connection_error` - Handle connection error

---

### 3.4 Image Generation Service Tests (test_image_gen_service.py)

#### Test Cases:

**DalleProvider.is_available**
- ✅ `test_dalle_available_with_key` - Return True when configured
- ✅ `test_dalle_unavailable_without_key` - Return False without key

**DalleProvider.generate()**
- ✅ `test_dalle_generate_success` - Generate image successfully
- ✅ `test_dalle_generate_returns_url` - Return image URL
- ✅ `test_dalle_generate_revised_prompt` - Return revised prompt
- ✅ `test_dalle_generate_custom_size` - Apply custom size
- ✅ `test_dalle_generate_hd_quality` - Apply HD quality
- ✅ `test_dalle_generate_vivid_style` - Apply vivid style
- ✅ `test_dalle_generate_natural_style` - Apply natural style
- ✅ `test_dalle_generate_rate_limit` - Handle rate limit error
- ✅ `test_dalle_generate_content_policy` - Handle content policy violation
- ✅ `test_dalle_generate_api_error` - Handle API error

**StabilityProvider.generate()**
- ✅ `test_stability_generate_success` - Generate image successfully
- ✅ `test_stability_generate_returns_data` - Return image bytes (base64)
- ✅ `test_stability_generate_custom_size` - Apply custom size
- ✅ `test_stability_generate_hd_quality` - More steps for HD
- ✅ `test_stability_generate_rate_limit` - Handle rate limit
- ✅ `test_stability_generate_timeout` - Handle timeout error
- ✅ `test_stability_generate_api_error` - Handle API error

**ImageGenerationService.generate()**
- ✅ `test_generate_dalle_provider` - Use DALL-E provider
- ✅ `test_generate_stability_provider` - Use Stability provider
- ✅ `test_generate_default_provider` - Use default provider
- ✅ `test_generate_fallback_provider` - Fallback when primary unavailable
- ✅ `test_generate_no_provider` - Error when no providers available

---

### 3.5 Storage Service Tests (test_storage_service.py)

#### Test Cases:

**LocalStorageProvider.upload_image()**
- ✅ `test_local_upload_success` - Upload image to local filesystem
- ✅ `test_local_upload_creates_thumbnail` - Create thumbnail
- ✅ `test_local_upload_returns_urls` - Return image and thumbnail URLs
- ✅ `test_local_upload_custom_filename` - Use custom filename
- ✅ `test_local_upload_without_thumbnail` - Skip thumbnail creation

**LocalStorageProvider.delete_image()**
- ✅ `test_local_delete_success` - Delete image and thumbnail
- ✅ `test_local_delete_missing_file` - Handle missing file gracefully

**LocalStorageProvider.download_from_url()**
- ✅ `test_local_download_success` - Download image from URL
- ✅ `test_local_download_not_found` - Handle 404 response
- ✅ `test_local_download_timeout` - Handle timeout error

**S3StorageProvider.upload_image()**
- ✅ `test_s3_upload_success` - Upload to S3/R2
- ✅ `test_s3_upload_creates_thumbnail` - Upload thumbnail
- ✅ `test_s3_upload_returns_keys` - Return S3 keys
- ✅ `test_s3_upload_public_url` - Return correct public URL
- ✅ `test_s3_upload_client_error` - Handle boto3 ClientError

**S3StorageProvider.delete_image()**
- ✅ `test_s3_delete_success` - Delete from S3
- ✅ `test_s3_delete_thumbnail` - Also delete thumbnail

**StorageService.upload_from_url()**
- ✅ `test_upload_from_url_success` - Download and upload
- ✅ `test_upload_from_url_download_failure` - Handle download failure

---

## 4. Core Tests (test_core/)

### 4.1 Security Tests (test_security.py)

#### Test Cases:

**Password Hashing**
- ✅ `test_hash_password` - Hash a password with bcrypt
- ✅ `test_hash_password_different_each_time` - Verify salt is random
- ✅ `test_verify_password_success` - Verify correct password
- ✅ `test_verify_password_failure` - Reject incorrect password
- ✅ `test_verify_password_truncates_at_72_bytes` - Handle long passwords

**JWT Tokens - Access Token**
- ✅ `test_create_access_token` - Create access token
- ✅ `test_create_access_token_payload` - Verify payload structure
- ✅ `test_create_access_token_custom_expiry` - Custom expiration time
- ✅ `test_create_access_token_additional_claims` - Add custom claims

**JWT Tokens - Refresh Token**
- ✅ `test_create_refresh_token` - Create refresh token
- ✅ `test_create_refresh_token_longer_expiry` - Longer expiration (7 days)

**JWT Tokens - Token Pair**
- ✅ `test_create_token_pair` - Create both access and refresh
- ✅ `test_token_pair_structure` - Verify TokenPair model

**JWT Tokens - Decoding**
- ✅ `test_decode_token_valid` - Decode valid token
- ✅ `test_decode_token_invalid` - Return None for invalid token
- ✅ `test_decode_token_expired` - Return None for expired token
- ✅ `test_decode_token_wrong_secret` - Return None for wrong secret

**JWT Tokens - Verification**
- ✅ `test_verify_token_access` - Verify access token
- ✅ `test_verify_token_refresh` - Verify refresh token
- ✅ `test_verify_token_wrong_type` - Reject wrong token type
- ✅ `test_verify_token_expired` - Reject expired token

**Utility Functions**
- ✅ `test_generate_api_key` - Generate secure API key
- ✅ `test_generate_verification_token` - Generate verification token

---

### 4.2 Middleware Tests (test_middleware.py)

#### Test Cases:

**CORS Middleware**
- ✅ `test_cors_allows_configured_origins` - Allow configured origins
- ✅ `test_cors_blocks_unconfigured_origins` - Block other origins
- ✅ `test_cors_preflight_request` - Handle OPTIONS preflight

**Logging Middleware**
- ✅ `test_logging_middleware_logs_requests` - Log all requests
- ✅ `test_logging_middleware_includes_status` - Log response status
- ✅ `test_logging_middleware_includes_duration` - Log request duration

---

### 4.3 Dependencies Tests (test_dependencies.py)

#### Test Cases:

**get_current_user()**
- ✅ `test_get_current_user_valid_token` - Return user for valid token
- ✅ `test_get_current_user_no_token` - Raise 401 without token
- ✅ `test_get_current_user_invalid_token` - Raise 401 for invalid token
- ✅ `test_get_current_user_expired_token` - Raise 401 for expired token
- ✅ `test_get_current_user_user_not_found` - Raise 401 if user deleted
- ✅ `test_get_current_user_inactive_user` - Raise 401 if user inactive

**get_optional_user()**
- ✅ `test_get_optional_user_with_token` - Return user if token provided
- ✅ `test_get_optional_user_without_token` - Return None if no token

**get_db()**
- ✅ `test_get_db_session` - Provide database session
- ✅ `test_get_db_closes_session` - Close session after request

---

### 4.4 Exceptions Tests (test_exceptions.py)

#### Test Cases:

**Custom Exception Handlers**
- ✅ `test_http_exception_handler` - Handle HTTPException
- ✅ `test_validation_error_handler` - Handle Pydantic validation errors
- ✅ `test_generic_exception_handler` - Handle unexpected exceptions
- ✅ `test_404_not_found_handler` - Custom 404 response

---

## 5. Model Tests (test_models/)

### 5.1 User Model Tests (test_user_model.py)

#### Test Cases:

**User Model**
- ✅ `test_user_creation` - Create user with all fields
- ✅ `test_user_defaults` - Verify default values
- ✅ `test_user_email_lowercase` - Email stored in lowercase
- ✅ `test_user_increment_generation_count` - Increment method works
- ✅ `test_user_preferences_default` - Default empty dict for preferences
- ✅ `test_user_relationships` - Verify generations relationship

---

### 5.2 Generation Model Tests (test_generation_model.py)

#### Test Cases:

**Generation Model**
- ✅ `test_generation_creation` - Create generation with all fields
- ✅ `test_generation_defaults` - Verify default values
- ✅ `test_generation_metadata_default` - Default empty dict for metadata

**Generation Status Methods**
- ✅ `test_mark_processing` - mark_processing() method
- ✅ `test_mark_enhancing` - mark_enhancing() method
- ✅ `test_mark_generating` - mark_generating() method
- ✅ `test_mark_uploading` - mark_uploading() method
- ✅ `test_mark_completed` - mark_completed() method with URLs
- ✅ `test_mark_failed` - mark_failed() method with error

**Generation Properties**
- ✅ `test_generation_duration` - Calculate duration if completed
- ✅ `test_generation_duration_none` - Return None if not completed

---

## 6. Background Task Tests (test_tasks/)

### 6.1 Generation Tasks Tests (test_generation_tasks.py)

#### Test Cases:

**process_generation_task()**
- ✅ `test_process_generation_task_success` - Full workflow succeeds
- ✅ `test_process_generation_task_with_enhancement` - Claude enhancement works
- ✅ `test_process_generation_task_without_enhancement` - Skip enhancement
- ✅ `test_process_generation_task_not_found` - Handle missing generation
- ✅ `test_process_generation_task_already_processed` - Skip if already done
- ✅ `test_process_generation_task_dalle_failure` - Handle DALL-E failure
- ✅ `test_process_generation_task_storage_failure` - Handle storage failure
- ✅ `test_process_generation_task_marks_failed` - Mark as failed on error
- ✅ `test_process_generation_task_retries` - Verify retry behavior
- ✅ `test_process_generation_task_updates_user_count` - Increment user count
- ✅ `test_process_generation_task_publishes_updates` - Publish to Redis

---

### 6.2 Cleanup Tasks Tests (test_cleanup_tasks.py)

#### Test Cases:

**cleanup_failed_generations()**
- ✅ `test_cleanup_old_failed_generations` - Delete failed >24h old
- ✅ `test_cleanup_stuck_generations` - Mark stuck as failed
- ✅ `test_cleanup_deletes_from_storage` - Remove images from storage
- ✅ `test_cleanup_skips_recent_failed` - Don't delete recent failures
- ✅ `test_cleanup_skips_recent_processing` - Don't mark recent as stuck
- ✅ `test_cleanup_returns_counts` - Return counts of cleaned items

---

## 7. Test Coverage Goals

### Minimum Coverage Targets:
- **Overall**: 85%+
- **Services**: 90%+
- **API Endpoints**: 90%+
- **Core (Security, Middleware)**: 95%+
- **Models**: 80%+
- **Tasks**: 85%+

### Coverage Exclusions:
- `__init__.py` files
- Configuration files
- Migrations
- Type stubs

---

## 8. Testing Tools & Libraries

### Required Packages:
```toml
[tool.poetry.group.test.dependencies]
pytest = "^8.0.0"
pytest-asyncio = "^0.23.0"
pytest-cov = "^6.0.0"
pytest-mock = "^3.14.0"
httpx = "^0.28.0"  # For TestClient
faker = "^30.0.0"  # Generate test data
freezegun = "^1.5.0"  # Mock datetime
responses = "^0.25.0"  # Mock external APIs
```

### Configuration (pytest.ini):
```ini
[pytest]
asyncio_mode = auto
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
    unit: marks tests as unit tests
addopts =
    --strict-markers
    --cov=app
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=85
```

---

## 9. Test Execution Strategy

### Running Tests:
```bash
# All tests
poetry run pytest

# Specific module
poetry run pytest tests/test_api/test_auth.py

# Specific test
poetry run pytest tests/test_api/test_auth.py::test_register_success

# With coverage
poetry run pytest --cov=app --cov-report=html

# Unit tests only
poetry run pytest -m unit

# Skip slow tests
poetry run pytest -m "not slow"
```

### CI/CD Integration:
- Run on every push and PR
- Fail build if coverage < 85%
- Fail build if any test fails
- Generate coverage report artifact

---

## 10. Mock Strategy

### External Services to Mock:
1. **Anthropic API** - Mock all Claude API calls
2. **OpenAI API** - Mock all DALL-E API calls
3. **Stability API** - Mock all Stability AI calls
4. **Redis** - Use fakeredis for pub/sub testing
5. **Celery** - Mock `.delay()` calls
6. **S3/Boto3** - Use moto library for S3 mocking
7. **HTTP Requests** - Use responses library

### Mock Examples:
```python
@pytest.fixture
def mock_dalle_api(monkeypatch):
    """Mock OpenAI DALL-E API."""
    def mock_generate(*args, **kwargs):
        return MagicMock(
            data=[MagicMock(
                url="https://example.com/image.png",
                revised_prompt="Enhanced prompt"
            )]
        )

    monkeypatch.setattr(
        "openai.OpenAI.images.generate",
        mock_generate
    )
```

---

## 11. Data Factories

### Using Faker for Test Data:
```python
import pytest
from faker import Faker

fake = Faker()

@pytest.fixture
def user_data():
    """Generate random user data."""
    return {
        "email": fake.email(),
        "password": fake.password(length=12),
        "display_name": fake.name(),
    }

@pytest.fixture
def generation_data():
    """Generate random generation data."""
    return {
        "prompt": fake.text(max_nb_chars=200),
        "style": fake.random_element(["vivid", "natural"]),
        "size": "1024x1024",
        "quality": "standard",
    }
```

---

## 12. Implementation Priority

### Phase 1 (High Priority):
1. ✅ Set up conftest.py with all fixtures
2. ✅ Core security tests (JWT, password hashing)
3. ✅ Authentication API tests (register, login, refresh)
4. ✅ User service tests

### Phase 2 (Medium Priority):
5. ✅ Generation API tests (create, get, delete)
6. ✅ Generation service tests
7. ✅ Gallery API tests
8. ✅ Model tests (User, Generation)

### Phase 3 (Lower Priority):
9. ✅ Claude service tests (with mocks)
10. ✅ Image generation service tests (with mocks)
11. ✅ Storage service tests
12. ✅ Chat API tests
13. ✅ WebSocket tests

### Phase 4 (Final):
14. ✅ Background task tests
15. ✅ Middleware tests
16. ✅ Exception handler tests
17. ✅ Integration tests

---

## 13. Special Test Scenarios

### Edge Cases to Cover:
- ⚠️ **Concurrent requests** - Multiple users creating generations simultaneously
- ⚠️ **Database rollback** - Transaction failures and rollbacks
- ⚠️ **Rate limiting** - User hitting limits exactly
- ⚠️ **Token expiration** - Token expires mid-request
- ⚠️ **Large payloads** - Max-size prompts, images
- ⚠️ **Unicode handling** - Emojis in prompts, names
- ⚠️ **Network timeouts** - External API timeouts
- ⚠️ **Celery task retry** - Task fails and retries
- ⚠️ **Storage failures** - S3 unavailable
- ⚠️ **Database connection loss** - Reconnection logic

---

## 14. Performance Tests (Optional)

### Load Testing:
- ⚙️ Test 100 concurrent users
- ⚙️ Test 1000 generations created per minute
- ⚙️ Test WebSocket with 500 concurrent connections
- ⚙️ Test database query performance

### Tools:
- Locust for load testing
- pytest-benchmark for micro-benchmarks

---

## Summary

This comprehensive test plan covers:
- **~280+ test cases** across all backend components
- **6 test modules** (API, Services, Core, Models, Tasks, Integration)
- **85%+ code coverage target**
- **Mock strategy** for all external dependencies
- **CI/CD integration** ready
- **Phase-by-phase implementation** plan

The plan ensures thorough testing of:
✅ Authentication & Authorization
✅ Image Generation Workflow
✅ AI Service Integration (Claude, DALL-E)
✅ File Storage (Local, S3, R2)
✅ Background Task Processing
✅ Real-time WebSocket Updates
✅ Rate Limiting & Error Handling
✅ Database Operations
✅ Security (JWT, Password Hashing)

---

**Next Steps:**
1. Review and approve this plan
2. Begin Phase 1 implementation (conftest.py + security tests)
3. Iterate through phases 2-4
4. Achieve 85%+ coverage
5. Integrate with CI/CD pipeline
