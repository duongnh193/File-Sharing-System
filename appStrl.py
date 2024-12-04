import streamlit as st
import bcrypt
import os
import json
import time

# css
st.markdown(
    """
    <style>
    /* Thanh bar trên đầu */
    .header-bar {
        background-color: #4CAF50;
        padding: 10px;
        display: flex;
        justify-content: space-between;
        color: white;
        font-size: 18px;
        font-weight: bold;
    }

    /* Nút đăng xuất */
    .logout-btn {
        background-color: #f44336;
        border: none;
        color: white;
        padding: 10px 20px;
        cursor: pointer;
    }

    /* Chào mừng */
    .welcome-text {
        font-size: 24px;
        margin-top: 20px;
        color: #4CAF50;
        text-align: center;
    }

    /* Hiển thị tên hệ thống chia sẻ file ở giữa */
    .center-header {
        text-align: center;
        font-size: 24px;
        font-weight: bold;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True
)

# folder 
UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# save user ifor
def save_user(username, password):
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    with open(".streamlit/data/users.txt", "a") as file:
        file.write(f"{username},{hashed.decode()}\n")

# load user infor
def load_users():
    users = {}
    if os.path.exists(".streamlit/data/users.txt"):
        with open(".streamlit/data/users.txt", "r") as file:
            for line in file:
                username, hashed = line.strip().split(",")
                users[username] = hashed
    return users

def register():
    username = st.text_input("Tên đăng nhập")
    password = st.text_input("Mật khẩu", type="password")
    if st.button("Đăng ký"):
        users = load_users()
        if username in users:
            st.warning("Tên đăng nhập đã tồn tại!")
        else:
            save_user(username, password)
            st.success("Đăng ký thành công, mời bạn đăng nhập!")

def login():
    username = st.text_input("Tên đăng nhập")
    password = st.text_input("Mật khẩu", type="password")
    if st.button("Đăng nhập"):
        users = load_users()
        if username in users and bcrypt.checkpw(password.encode(), users[username].encode()):
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.session_state["welcome_message"] = True
            st.success("Đăng nhập thành công!")
            time.sleep(0.5)
            st.rerun()
        elif not username or not password:
            st.warning("Vui lòng điền tên đăng nhập và mật khẩu.")
        else:
            st.error("Sai tên đăng nhập hoặc mật khẩu!")

def logout():
    st.session_state["logged_in"] = False
    st.session_state["username"] = None
    st.session_state["logout_message"] = True
    st.rerun()

PERMISSION_FILE = "permissions.json"

#load json
def load_permissions():
    try:
        with open("permissions.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# save json   
def save_permissions(permissions):
    with open("permissions.json", "w") as f:
        json.dump(permissions, f, indent=4)

# update json file
def update_file_permission(username, file_name, is_public):
    permissions = load_permissions()
    if username not in permissions:
        permissions[username] = {}
    if file_name not in permissions[username]:
        permissions[username][file_name] = {
            "is_public": is_public,
            "allowed_users": [],  
            "requests": []       
        }
    else:
        permissions[username][file_name]["is_public"] = is_public
    if "allowed_users" not in permissions[username][file_name]:
            permissions[username][file_name]["allowed_users"] = []
    save_permissions(permissions)

# check request
def handle_permission_request(file_name, requester):
    # check allow list
    permissions = load_permissions()
    user_permissions = permissions.get(st.session_state["username"], {})
    
    if file_name in user_permissions:
        file_data = user_permissions[file_name]
        if requester in file_data["requests"]:
            file_data["allowed_users"].append(requester)
            file_data["requests"].remove(requester) 
            save_permissions(permissions)
        else:
            st.error(f"{requester} không có yêu cầu cấp quyền đối với file '{file_name}'.")
    else:
        st.error(f"File '{file_name}' không tồn tại trong danh sách của bạn.")

# save file uploaded
def save_uploaded_file(uploaded_file):
    user_folder = os.path.join(UPLOAD_FOLDER, st.session_state["username"])
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)

    file_path = os.path.join(user_folder, uploaded_file.name)
    
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    is_public = st.checkbox("Cho phép tải file này công khai", value=True)

    # update permisssion in json
    permissions = load_permissions()
    username = st.session_state["username"]
    if username not in permissions:
        permissions[username] = {}
    
    permissions[username][uploaded_file.name] = {
        "is_public": is_public,
        "allowed_users": [],  
        "requests": []
    }
    save_permissions(permissions)

    st.success(f"File '{uploaded_file.name}' đã được tải lên và thông tin quyền được cập nhật!")

# main function
def main():
    st.markdown(
        """
        <div class="header-bar">
            <div class="center-header">Hệ thống chia sẻ file</div>
        </div>
        """.format(
            f"<button class='logout-btn' onclick='window.location.reload()'>Đăng xuất</button>"
            if st.session_state.get("logged_in") else ""
        ),
        unsafe_allow_html=True
    )
    st.markdown(
        """
        <style>
        .logout-button {
            position: absolute;
            top: 10px;
            right: 10px;
            background-color: #f44336;
            border: none;
            color: white;
            padding: 10px 20px;
            cursor: pointer;
        }
        </style>
        """, unsafe_allow_html=True
    )   

    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if st.session_state.get("logout_message"):
        st.success("Đăng xuất thành công!")
        time.sleep(0.5)
        st.session_state["logout_message"] = False
        st.rerun()

    if st.session_state.get("logged_in"):
        if st.button("Đăng xuất", key="logout_button"):
            logout()
            st.session_state["logout_message"] = True
        
        # upload file
        menu = st.sidebar.radio("Menu", ["Tải lên", "Tải xuống", "Xem file đã upload", "Xử lý yêu cầu cấp quyền"])

        if menu == "Tải lên":
            st.subheader("Tải lên file")
            uploaded_file = st.file_uploader("Chọn file để tải lên")
            if uploaded_file is not None:
                save_uploaded_file(uploaded_file)

        elif menu == "Tải xuống":
            st.subheader("Tải xuống file")
            permissions = load_permissions()

            # get user list
            user_folders = [f for f in os.listdir(UPLOAD_FOLDER) if os.path.isdir(os.path.join(UPLOAD_FOLDER, f))]
            if st.session_state["username"] in user_folders:
                user_folders.remove(st.session_state["username"])

            if not user_folders:
                st.info("Không có người dùng nào khác để tải file.")
                return

            selected_user = st.selectbox("Chọn người dùng để tải file", user_folders)
            user_folder_path = os.path.join(UPLOAD_FOLDER, selected_user)

            # Danh sách file của người dùng được chọn
            user_files = os.listdir(user_folder_path)
            restricted_files = []
            if user_files:
                for file_name in user_files:
                    file_permission = permissions.get(selected_user, {}).get(file_name, {})
                    
                    # Kiểm tra quyền của file
                    allowed_users = file_permission.get("allowed_users", [])
                    if file_permission.get("is_public", False):  
                        st.markdown(
                            f"<span style='color: green;'>File (Công khai):</span> {file_name}",
                            unsafe_allow_html=True,
                        )
                        file_path = os.path.join(user_folder_path, file_name)
                        with open(file_path, "rb") as file:
                            st.download_button(
                                label="Tải file về",
                                data=file,
                                file_name=file_name
                            )
                    elif st.session_state["username"] in file_permission.get("allowed_users", []):
                        st.markdown(
                            f"<span style='color: red;'>File (Được cấp quyền):</span> {file_name}",
                            unsafe_allow_html=True,
                        )
                        st.write(f"File: {file_name}")
                        file_path = os.path.join(user_folder_path, file_name)
                        with open(file_path, "rb") as file:
                            st.download_button(
                                label="Tải file về",
                                data=file,
                                file_name=file_name
                            )
                    else:
                        restricted_files.append(file_name)

            if restricted_files:
                st.write("Các file yêu cầu quyền:")
                selected_file = st.selectbox("Chọn file cần xin quyền", restricted_files)
                if st.button("Xin cấp quyền"):
                    permissions[selected_user][selected_file]["requests"].append(st.session_state["username"])
                    save_permissions(permissions)
                    st.success("Đã gửi yêu cầu cấp quyền!")

        elif menu == "Xem file đã upload":
            st.subheader("Danh sách file của bạn")

            # Xác định thư mục của người dùng
            user_folder = os.path.join(UPLOAD_FOLDER, st.session_state["username"])

            # Kiểm tra thư mục tồn tại
            if not os.path.exists(user_folder):
                st.info("Bạn chưa upload file nào.")
            else:
                user_files = os.listdir(user_folder)
                if user_files:
                    st.write("Danh sách file của bạn:")
                    permissions = load_permissions()
                    for file in user_files:
                        st.write(f"- {file}")
                        
                        # Hiển thị checkbox để chỉnh sửa quyền file
                        file_permission = permissions.get(st.session_state["username"], {}).get(file, {"is_public": True})
                        is_public = file_permission.get("is_public", True)
                        new_permission = st.checkbox(f"Cho phép tải công khai: {file}", value=is_public, key=file)

                        # Cập nhật quyền nếu thay đổi
                        if new_permission != is_public:
                            update_file_permission(st.session_state["username"], file, new_permission)
                            success_message = st.empty()
                            success_message.success(f"Cập nhật quyền của file '{file}' thành công!")
                            time.sleep(1)
                            success_message.empty()
                else:
                    st.info("Bạn chưa upload file nào.")

        elif menu == "Xử lý yêu cầu cấp quyền":
            st.subheader("Các yêu cầu cấp quyền cho file của bạn")
            permissions = load_permissions()
            user_permissions = permissions.get(st.session_state["username"], {})

            # Duyệt qua các file của người dùng và kiểm tra yêu cầu cấp quyền
            for file_name, file_data in user_permissions.items():
                if file_data["requests"]:
                    st.write(f"File: {file_name}")
                    st.write("Danh sách yêu cầu:")
                    for requester in file_data["requests"]:
                        st.write(f"- {requester}")
                        if st.button(f"Cấp quyền cho {requester}", key=f"{file_name}_{requester}"):
                            handle_permission_request(file_name, requester)
                            success_message = st.empty()
                            success_message.success(f"Đã cấp quyền cho {requester} tải file '{file_name}'!")
                            time.sleep(1)
                            success_message.empty()
    else:
        menu = st.radio("Chọn", ["Đăng nhập", "Đăng ký"], horizontal=True)
        if menu == "Đăng nhập":
            login()
        elif menu == "Đăng ký":
            register()

if __name__ == "__main__":
    main()
