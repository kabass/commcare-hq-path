function(doc) {
    if (doc.doc_type === "FormExportDataSchema" || doc.doc_type === "FormInferredSchema") {
        emit([doc.domain, doc.doc_type, doc.app_id, doc.xmlns, doc.created_on], null);
    } else if (doc.doc_type === "CaseExportDataSchema" || doc.doc_type === "CaseInferredSchema") {
        emit([doc.domain, doc.doc_type, doc.case_type, doc.created_on], null);
    }
}
