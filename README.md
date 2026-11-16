
1. **Таблица `users` (Пользователи)**
   * `id` 
   * `username` 
   * `hashed_password` 

2. **Таблица `teachers` (Педагоги)**
   * `id` 
   * `name` 
   * `subject` 
   * `phone`

3. **Таблица `applications` (Заявки)**
   * `id` 
   * `user_id` `users`
   * `teacher_id``teachers`
   * `message`
   * `created_at`
