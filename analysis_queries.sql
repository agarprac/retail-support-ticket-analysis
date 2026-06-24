-- support ticket analysis
-- table: support_tickets (sqlite db: tickets.db)

-- overall numbers, just to get a feel for the data
SELECT
    COUNT(*) AS total_tickets,
    ROUND(AVG(resolution_minutes), 1) AS avg_resolution_minutes,
    SUM(repeat_visit_needed) AS tickets_with_repeat_visit,
    ROUND(100.0 * SUM(repeat_visit_needed) / COUNT(*), 1) AS repeat_visit_rate_percent
FROM support_tickets;


-- ticket volume by issue type
SELECT
    issue_type,
    COUNT(*) AS ticket_count,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM support_tickets), 1) AS percent_of_all_tickets
FROM support_tickets
GROUP BY issue_type
ORDER BY ticket_count DESC;


-- which issues have the worst repeat visit rate
SELECT
    issue_type,
    COUNT(*) AS ticket_count,
    ROUND(AVG(resolution_minutes), 1) AS avg_resolution_minutes,
    ROUND(100.0 * SUM(repeat_visit_needed) / COUNT(*), 1) AS repeat_visit_rate_percent
FROM support_tickets
GROUP BY issue_type
ORDER BY repeat_visit_rate_percent DESC;


-- the main question: does having a kb article actually change anything
SELECT
    CASE WHEN kb_article_existed = 1 THEN 'Knowledge base article existed'
         ELSE 'No knowledge base article' END AS kb_status,
    COUNT(*) AS ticket_count,
    ROUND(AVG(resolution_minutes), 1) AS avg_resolution_minutes,
    ROUND(100.0 * SUM(repeat_visit_needed) / COUNT(*), 1) AS repeat_visit_rate_percent
FROM support_tickets
GROUP BY kb_status;


-- of the issues with no article, which ones are burning the most hours
-- (counting a repeat visit as roughly a second visit's worth of time)
SELECT
    issue_type,
    device_category,
    COUNT(*) AS ticket_count,
    ROUND(100.0 * SUM(repeat_visit_needed) / COUNT(*), 1) AS repeat_visit_rate_percent,
    ROUND(SUM(resolution_minutes * (1 + repeat_visit_needed)) / 60.0, 1) AS estimated_total_hours
FROM support_tickets
WHERE kb_article_existed = 0
GROUP BY issue_type, device_category
ORDER BY estimated_total_hours DESC;


-- checking if this is a company wide issue or just one or two stores
SELECT
    store_location,
    COUNT(*) AS ticket_count,
    ROUND(100.0 * SUM(repeat_visit_needed) / COUNT(*), 1) AS repeat_visit_rate_percent
FROM support_tickets
GROUP BY store_location
ORDER BY repeat_visit_rate_percent DESC;


-- priority mix on the issues with no kb article
SELECT
    issue_type,
    priority,
    COUNT(*) AS ticket_count
FROM support_tickets
WHERE kb_article_existed = 0
GROUP BY issue_type, priority
ORDER BY issue_type, priority;


-- monthly trend for the 3 problem issues - getting better or worse over time?
SELECT
    strftime('%Y-%m', created_date) AS month,
    issue_type,
    COUNT(*) AS ticket_count,
    ROUND(100.0 * SUM(repeat_visit_needed) / COUNT(*), 1) AS repeat_visit_rate_percent
FROM support_tickets
WHERE kb_article_existed = 0
GROUP BY month, issue_type
ORDER BY month, issue_type;
