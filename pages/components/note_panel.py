import streamlit as st
from loguru import logger
from streamlit_monaco import st_monaco  # type: ignore

from open_notebook.domain.notebook import Note
from pages.stream_app.utils import convert_source_references


def note_panel(note_id, notebook_id=None):
    note: Note = Note.get(note_id)
    if not note:
        raise ValueError(f"Note not fonud {note_id}")
    t_preview, t_edit = st.tabs(["Preview", "Edit"])
    with t_preview:
        st.subheader(note.title)
        st.markdown(convert_source_references(note.content))
    with t_edit:
        note.title = st.text_input("Title", value=note.title)
        note.content = st_monaco(
            value=note.content, height="600px", language="markdown"
        )
        if st.button("Save", key=f"pn_edit_note_{note.id or 'new'}"):
            logger.debug("Editing note")
            note.save()
            if not note.id and notebook_id:
                note.add_to_notebook(notebook_id)
            st.rerun()
    if st.button("Delete", type="primary", key=f"delete_note_{note.id or 'new'}"):
        logger.debug("Deleting note")
        note.delete()
        st.rerun()
