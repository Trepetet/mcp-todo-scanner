/**
 * Модуль для управления задачами (Todo Manager)
 * @module todoManager
 */

// Константы приложения
const STORAGE_KEY = 'todo_tasks';
const MAX_TASKS = 1000;

/**
 * Класс для управления списком задач
 */
class TodoManager {
    constructor() {
        /** @type {Array} Список задач */
        this.tasks = [];
        this.loadTasks();
    }

    /**
     * Загрузка задач из localStorage
     * TODO: Добавить синхронизацию с удаленным сервером
     * TODO: Добавить обработку ошибок при превышении лимита localStorage
     */
    loadTasks() {
        try {
            const savedTasks = localStorage.getItem(STORAGE_KEY);
            if (savedTasks) {
                this.tasks = JSON.parse(savedTasks);
                console.log(`Загружено ${this.tasks.length} задач`);
            } else {
                this.tasks = [];
            }
        } catch (error) {
            // FIXME: При ошибке парсинга JSON теряются все задачи пользователя
            // Нужно добавить восстановление из backup
            console.error('Ошибка загрузки задач:', error);
            this.tasks = [];
        }
    }

    /**
     * Сохранение задач в localStorage
     * BUG: При сохранении очень большого списка (>5MB) может превысить лимит localStorage
     * Нужно реализовать пагинацию или сжатие данных
     */
    saveTasks() {
        try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(this.tasks));
            console.log('Задачи сохранены');
        } catch (error) {
            console.error('Ошибка сохранения:', error);
        }
    }

    /**
     * Добавление новой задачи
     * @param {string} title - Заголовок задачи
     * @param {string} description - Описание задачи
     * @returns {Object} Созданная задача
     * 
     * TODO: Добавить валидацию длины заголовка
     * TODO: Добавить проверку на дубликаты задач
     */
    addTask(title, description = '') {
        // FIXME: Не проверяется наличие title, может быть пустая строка
        if (this.tasks.length >= MAX_TASKS) {
            throw new Error('Достигнут максимальный лимит задач');
        }

        const task = {
            id: Date.now(),
            title: title,
            description: description,
            completed: false,
            createdAt: new Date().toISOString(),
            // TODO: Добавить поле priority (low, medium, high)
            // TODO: Добавить поле dueDate (срок выполнения)
            priority: 'medium'
        };

        this.tasks.push(task);
        this.saveTasks();
        return task;
    }

    /**
     * Удаление задачи по ID
     * @param {number} taskId - ID задачи
     * @returns {boolean} Результат удаления
     * 
     * BUG: При удалении несуществующей задачи возвращает false,
     * но пользователь не видит сообщения об ошибке
     */
    deleteTask(taskId) {
        const initialLength = this.tasks.length;
        this.tasks = this.tasks.filter(task => task.id !== taskId);
        
        if (this.tasks.length === initialLength) {
            console.warn(`Задача с ID ${taskId} не найдена`);
            return false;
        }
        
        this.saveTasks();
        return true;
    }

    /**
     * Переключение статуса выполнения задачи
     * @param {number} taskId - ID задачи
     * @returns {Object|null} Обновленная задача или null
     * 
     * TODO: Добавить анимацию при переключении статуса
     * TODO: Добавить историю изменений статуса
     */
    toggleTaskStatus(taskId) {
        const task = this.tasks.find(t => t.id === taskId);
        
        // FIXME: При быстром двойном переключении может возникнуть race condition
        if (task) {
            task.completed = !task.completed;
            task.updatedAt = new Date().toISOString();
            this.saveTasks();
            return task;
        }
        
        return null;
    }

    /**
     * Поиск задач по тексту
     * @param {string} searchText - Текст для поиска
     * @returns {Array} Отфильтрованные задачи
     * 
     * FIXME: Поиск регистрозависимый, нужно добавить toLowerCase()
     * TODO: Добавить поиск по датам
     * TODO: Добавить фильтрацию по статусу выполнения
     */
    searchTasks(searchText) {
        if (!searchText) {
            return this.tasks;
        }

        // BUG: Поиск работает только по заголовку, игнорирует описание
        return this.tasks.filter(task => 
            task.title.includes(searchText) || 
            (task.description && task.description.includes(searchText))
        );
    }

    /**
     * Получение статистики по задачам
     * @returns {Object} Статистика
     * 
     * TODO: Добавить статистику по приоритетам
     * TODO: Добавить график выполнения по дням
     */
    getStats() {
        const total = this.tasks.length;
        const completed = this.tasks.filter(t => t.completed).length;
        const pending = total - completed;

        return {
            total,
            completed,
            pending,
            completionRate: total > 0 ? (completed / total * 100).toFixed(2) : 0
        };
    }
}

// Создание экземпляра менеджера
const todoManager = new TodoManager();

// Пример использования
try {
    // Добавление тестовых задач
    todoManager.addTask('Купить продукты', 'Молоко, хлеб, яйца');
    todoManager.addTask('Сделать домашнее задание', 'JavaScript, Python');
    
    // Получение статистики
    const stats = todoManager.getStats();
    console.log('Статистика задач:', stats);
    
    // Поиск задач
    const searchResults = todoManager.searchTasks('продукты');
    console.log('Результаты поиска:', searchResults);
    
} catch (error) {
    console.error('Ошибка в работе с задачами:', error);
}

// Экспорт для использования в других модулях
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TodoManager;
}