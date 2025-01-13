-- Report Management Functions

-- Search reports by criteria
CREATE OR REPLACE FUNCTION search_reports(
    p_search_text TEXT DEFAULT NULL,
    p_category_id UUID DEFAULT NULL,
    p_is_system BOOLEAN DEFAULT NULL,
    p_created_by UUID DEFAULT NULL,
    p_date_from TIMESTAMP DEFAULT NULL,
    p_date_to TIMESTAMP DEFAULT NULL,
    p_limit INTEGER DEFAULT 20,
    p_offset INTEGER DEFAULT 0
)
RETURNS TABLE (
    id UUID,
    name TEXT,
    description TEXT,
    category_name TEXT,
    template_type TEXT,
    is_system BOOLEAN,
    created_by UUID,
    created_at TIMESTAMP,
    total_count BIGINT
) AS $$
BEGIN
    RETURN QUERY
    WITH filtered_reports AS (
        SELECT 
            r.id,
            r.name,
            r.description,
            rc.name as category_name,
            rt.template_type,
            r.is_system,
            r.created_by,
            r.created_at
        FROM reports r
        JOIN report_categories rc ON r.category_id = rc.id
        JOIN report_templates rt ON r.template_id = rt.id
        WHERE 
            (p_search_text IS NULL OR 
             r.name ILIKE '%' || p_search_text || '%' OR 
             r.description ILIKE '%' || p_search_text || '%')
            AND (p_category_id IS NULL OR r.category_id = p_category_id)
            AND (p_is_system IS NULL OR r.is_system = p_is_system)
            AND (p_created_by IS NULL OR r.created_by = p_created_by)
            AND (p_date_from IS NULL OR r.created_at >= p_date_from)
            AND (p_date_to IS NULL OR r.created_at <= p_date_to)
            AND NOT r.is_deleted
    )
    SELECT 
        fr.*,
        COUNT(*) OVER() as total_count
    FROM filtered_reports fr
    ORDER BY fr.created_at DESC
    LIMIT p_limit
    OFFSET p_offset;
END;
$$ LANGUAGE plpgsql;

-- Get report details with template and category
CREATE OR REPLACE FUNCTION get_report_details(p_report_id UUID)
RETURNS TABLE (
    id UUID,
    name TEXT,
    description TEXT,
    category_id UUID,
    category_name TEXT,
    template_id UUID,
    template_name TEXT,
    template_type TEXT,
    template_data JSONB,
    parameters JSONB,
    is_system BOOLEAN,
    created_by UUID,
    created_at TIMESTAMP,
    updated_by UUID,
    updated_at TIMESTAMP,
    version INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        r.id,
        r.name,
        r.description,
        r.category_id,
        rc.name as category_name,
        r.template_id,
        rt.name as template_name,
        rt.template_type,
        rt.template_data,
        r.parameters,
        r.is_system,
        r.created_by,
        r.created_at,
        r.updated_by,
        r.updated_at,
        r.version
    FROM reports r
    JOIN report_categories rc ON r.category_id = rc.id
    JOIN report_templates rt ON r.template_id = rt.id
    WHERE r.id = p_report_id AND NOT r.is_deleted;
END;
$$ LANGUAGE plpgsql;

-- Clone report
CREATE OR REPLACE FUNCTION clone_report(
    p_report_id UUID,
    p_new_name TEXT,
    p_user_id UUID
)
RETURNS UUID AS $$
DECLARE
    v_new_report_id UUID;
BEGIN
    INSERT INTO reports (
        name,
        description,
        category_id,
        template_id,
        parameters,
        is_system,
        created_by,
        updated_by
    )
    SELECT 
        p_new_name,
        'Cloned from ' || r.name,
        r.category_id,
        r.template_id,
        r.parameters,
        FALSE, -- Cloned reports are never system reports
        p_user_id,
        p_user_id
    FROM reports r
    WHERE r.id = p_report_id AND NOT r.is_deleted
    RETURNING id INTO v_new_report_id;

    RETURN v_new_report_id;
END;
$$ LANGUAGE plpgsql;

-- Get report audit history
CREATE OR REPLACE FUNCTION get_report_audit_history(
    p_report_id UUID,
    p_limit INTEGER DEFAULT 20,
    p_offset INTEGER DEFAULT 0
)
RETURNS TABLE (
    id UUID,
    action TEXT,
    changes JSONB,
    performed_by UUID,
    performed_at TIMESTAMP,
    total_count BIGINT
) AS $$
BEGIN
    RETURN QUERY
    WITH audit_history AS (
        SELECT 
            ra.id,
            ra.action,
            ra.changes,
            ra.performed_by,
            ra.performed_at
        FROM report_audit ra
        WHERE ra.report_id = p_report_id
    )
    SELECT 
        ah.*,
        COUNT(*) OVER() as total_count
    FROM audit_history ah
    ORDER BY ah.performed_at DESC
    LIMIT p_limit
    OFFSET p_offset;
END;
$$ LANGUAGE plpgsql;

-- Soft delete reports
CREATE OR REPLACE FUNCTION soft_delete_reports(
    p_report_ids UUID[],
    p_user_id UUID
)
RETURNS INTEGER AS $$
DECLARE
    v_count INTEGER;
BEGIN
    UPDATE reports
    SET 
        is_deleted = TRUE,
        updated_by = p_user_id,
        updated_at = NOW()
    WHERE id = ANY(p_report_ids)
        AND NOT is_system -- Prevent deletion of system reports
        AND NOT is_deleted
    RETURNING COUNT(*) INTO v_count;

    RETURN v_count;
END;
$$ LANGUAGE plpgsql;
