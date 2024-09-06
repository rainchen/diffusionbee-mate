import html
import json
import re
import subprocess
import streamlit as st
import os


class History:
    def __init__(self, history_data, data_path=None):
        self.history_data = history_data
        self.data_path = data_path
        self._prompt_groups = {}

    @classmethod
    def load_from_path(cls, path):
        with open(path, "r") as f:
            history_data = json.load(f)
        return cls(history_data, path)

    @classmethod
    def load_from_json(cls, json_data):
        history_data = json.loads(json_data)
        return cls(history_data)

    def delete_image_by_job_id(self, img_job_id):
        groups_to_remove = []
        for group_id, group_data in self.history_data["history"].items():
            for img in group_data["imgs"]:
                if img["params"]["job_id"] == img_job_id:
                    group_data["imgs"].remove(img)
                    group_data["num_imgs"] -= 1
                    if group_data["num_imgs"] == 0:
                        groups_to_remove.append(group_id)
                    break
        for group_id in groups_to_remove:
            del self.history_data["history"][group_id]

    def save_to(self, path, indent=None):
        with open(path, "w") as f:
            json.dump(self.history_data, f, indent=indent)

    def list(self):
        return list(reversed(list(self.history_data["history"].values())))

    def group_by_prompt(self):
        self._prompt_groups = {}
        for item in self.list():
            prompt = item["params"]["prompt"]
            if prompt not in self._prompt_groups:
                self._prompt_groups[prompt] = []
            self._prompt_groups[prompt].append(item)
        return self._prompt_groups

    def get_prompt_groups(self):
        return self._prompt_groups

    def search(self, prompt_query):
        self._prompt_groups = {
            prompt: items
            for prompt, items in self._prompt_groups.items()
            if str.lower(prompt_query) in str.lower(prompt)
        }

    def total_images(self):
        return sum(len(self._prompt_groups[prompt]) for prompt in self._prompt_groups)

    def total_grouped_prompts(self):
        return len(self._prompt_groups)


def main():
    APP_NAME = "DiffusionBee Mate"

    history_path = os.path.join(
        os.path.expanduser("~"), ".diffusionbee", "history.json"
    )
    history = History.load_from_path(history_path)
    history.group_by_prompt()

    st.set_page_config(layout="wide", page_title=APP_NAME)
    ui_custom_css()

    ui_setup_sidebar(APP_NAME, history)

    ui_display_images(
        history,
        st.session_state.get("page_slider", 1),
        st.session_state.get("page_size_input", 10),
    )


def os_trash_file(file_path):
    if os.path.isfile(file_path):
        file_abspath = os.path.abspath(file_path)
        file_path_escaped = file_abspath.replace("\\", "\\\\").replace('"', '\\"')
        script = f'tell application "Finder" to delete POSIX file "{file_path_escaped}"'
        cmd = ["osascript", "-e", script]
        return subprocess.call(cmd, stdout=open(os.devnull, "w"))
    else:
        return 1


def ui_change_page_size():
    print("change page_size:", st.session_state["page_size_input"])
    if "page_slider" in st.session_state:
        del st.session_state["page_slider"]
    st.query_params["page"] = 1


def ui_custom_css():
    st.html(
        """ <style>
            .element-container:has(button > svg) ~ .element-container:has(.stButton) {
                position: absolute; top: 0; left: 0; width: 100%; height: 90%;
            }

            .element-container:has(button > svg) ~ .element-container:has(.stButton) > .stButton > button:has(div:empty) {
                position: absolute;top: 0;left: 0;width: 100%;height: 100%;border: none;opacity: 0;
            }
        </style>"""
    )


def ui_delete_image(history: History, img: dict):
    img_job_id = img["params"]["job_id"]
    img_path = img["params"]["generated_img"]
    print(f"Delete image by job_id: {img_job_id}, path: {img_path}")
    trash_image_result = os_trash_file(img_path)
    if trash_image_result == 0:
        history.save_to(history.data_path + ".backup.json")
        history.delete_image_by_job_id(img_job_id)
        history.save_to(history.data_path)


def ui_display_images(history: History, page, page_size):
    prompt_groups = history.get_prompt_groups()
    start_index = (page - 1) * int(page_size)
    end_index = start_index + int(page_size)
    current_prompts = list(prompt_groups.keys())[start_index:end_index]

    for prompt in current_prompts:
        st.markdown(f"##### {html.escape(prompt)}")

        if "negative_prompt" in prompt_groups[prompt][0]["params"]:
            st.html(
                f"<small style='color: grey'>negative prompt: {html.escape(prompt_groups[prompt][0]['params']['negative_prompt'])}</small>"
            )

        num_prompts_in_group = len(prompt_groups[prompt])
        num_columns = num_prompts_in_group
        cols_min_num = 5

        cols = st.columns(max(num_columns, cols_min_num))
        for i, item in enumerate(prompt_groups[prompt]):
            model = item["params"]["selected_sd_model"]
            cols[i].write(model)

        if num_prompts_in_group == 1:
            num_columns = len(prompt_groups[prompt][0]["imgs"])
        cols = st.columns(max(num_columns, cols_min_num))

        for prompt_idx, item in enumerate(prompt_groups[prompt]):
            for img_idx, img in enumerate(item["imgs"]):
                caption = "Seed: {seed} | Resolution: {img_width}x{img_height} | Steps: {num_steps} | Style: {selected_sd_style}".format(
                    **img["params"]
                )
                cols_idx = (
                    prompt_idx if num_columns == num_prompts_in_group else img_idx
                )
                img_placeholder = cols[cols_idx].container()
                img_placeholder.image(
                    img["image_url"], use_column_width=True, caption=caption
                )
                img_key = f"view_img_{img['params']['job_id']}"
                if img_placeholder.button("", key=img_key):
                    ui_view_image(history, img, img_key)

        st.write("---")


def ui_search_prompts():
    prompt_query = st.session_state["prompt_query"]
    print("search for:", prompt_query)
    if "page_slider" in st.session_state:
        del st.session_state["page_slider"]
    st.query_params["page"] = 1


def ui_setup_sidebar(APP_NAME, history: History):
    with st.sidebar:
        st.html("<a href='/' target='_self'>🏠</a>")
        st.title(APP_NAME)

        # Search
        with st.container(border=True):
            prompt_query_from_url = st.query_params.get("prompt_query", "")
            if "prompt_query" in st.session_state:
                prompt_query = st.session_state["prompt_query"]
            else:
                prompt_query = prompt_query_from_url
            prompt_query_input = st.text_input(
                "Search prompts",
                prompt_query,
                key="prompt_query",
                on_change=ui_search_prompts,
            )
            if prompt_query_input != prompt_query_from_url:
                st.query_params["prompt_query"] = prompt_query

            # Filter prompt_groups based on the search query
            history.search(prompt_query)

        # Pagination
        with st.container(border=True):
            default_page_size = 10
            page_size_from_url = int(
                st.query_params.get("page_size", default_page_size)
            )

            if (
                "page_size" in st.query_params
                and "page_size_input" not in st.session_state
            ):
                selected_page_size = page_size_from_url
            else:
                selected_page_size = int(
                    st.session_state.get("page_size_input", default_page_size)
                )
            page_size_value = st.text_input(
                "Page size",
                selected_page_size,
                key="page_size_input",
                on_change=ui_change_page_size,
            )
            page_size = int(page_size_value)

        # Page
        with st.container(border=True):
            page_from_url = int(st.query_params.get("page", 1))
            num_grouped_prompts = history.total_grouped_prompts()
            num_pages = (num_grouped_prompts + page_size - 1) // page_size

            if "page" in st.query_params and "page_slider" not in st.session_state:
                selected_page = page_from_url
            else:
                selected_page = st.session_state.get("page_slider", 1)
            if num_pages > 1:
                page = st.slider("Page", 1, num_pages, selected_page, key="page_slider")
            else:
                page = 1

            if selected_page != page_from_url:
                st.query_params["page"] = page

            if selected_page_size != page_size_from_url:
                st.query_params["page_size"] = page_size

        # Amount
        with st.container(border=True):
            total_images = history.total_images()
            num_grouped_prompts = history.total_grouped_prompts()
            st.write(f"Total images: {total_images}")
            st.write(f"Grouped prompts: {num_grouped_prompts}")


@st.dialog("Image Detail", width="large")
def ui_view_image(history: History, img, title):
    st.image(img["image_url"], use_column_width=True)
    cols_left, _, cols_right = st.columns([3, 6, 2])
    with cols_left:
        with st.popover("ℹ️ Image Params"):
            params_table = """
                | Params | Value |
                |-----------|-------|
                | Mode | {applet_name} |
                | Prompt | {prompt} |
                | Negative Prompt | {negative_prompt} |
                | Model | {selected_sd_model} |
                | Resolution | {img_width}x{img_height} |
                | Seed | {seed} |
                | Num Steps | {num_steps} |
                | Style | {selected_sd_style} |
                | Sampler | {scheduler} |
                | Guidance Scale | {guidance_scale} |
                | Controlnet Model | {controlnet_model} |
                | ControlNet Importance | {control_weight} |
                | LoRA 0 | {selected_sd_lora_0} |
                | LoRA 1 | {selected_sd_lora_1} |
                | LoRA 2 | {selected_sd_lora_2} |
                """
            param_keys = re.findall(r"{([^}]+)}", params_table)
            img_params = {
                key: str(img["params"].get(key, "N/A")).replace("\n", " ")
                for key in param_keys
            }
            st.markdown(params_table.format(**img_params))
    with cols_right:
        with st.popover("🗑️ Delete", use_container_width=True):
            if st.button("⚠️ Sure?", key="delete_image"):
                ui_delete_image(history, img)
                st.rerun()
            st.html("<small>⛔ Don't delete while DiffusionBee app is running</small>")


if __name__ == "__main__":
    main()
