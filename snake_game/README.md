# Gam rắn săn mồi
## Giới thiệu
Trò chơi nầy được xây dựng dựa trên game rắn săn mồi cổ điển và tích hợp thêm các tính năng khác để tăng trải nghiệm người chơi. Trò chơi được tạo ra bằng ngôn ngữ Python và sử dụng framework PyGame
## Tính năng nổi bật
- Chế độ chơi đa dạng: Người chơi được quyền chọn kích thướt bàn chơi cũng như chế độ tự chơi hoặc chế độ bot chơi.
- Hình ảnh đẹp mắt: Giao diện được thiết kế theo phong cách tết mang lại màu không khí vui vẻ khi chơi, người chơi.còn được quyền chọn giao diện của rắn.
- Âm nhạc sống động: Tích hợp âm nhạc khi chơi và ăn thức ăn đem lại trải nghiệm thú vị.
- Thay đổi ngôn ngữ: Đem lại trải nghiệm tốt nhất cho các tệp người chơi khác nhau.
## Cấu trúc thư mục
  * [snake/](./snake_game/snake)
   * [__init__.py](./snake_game/snake/__init__.py)
   * [settings.py](./snake_game/snake/settings.py)
   * [app.py](./snake_game/snake/app.py)
   * [core/](./snake_game/snake/core)
     * [__init__.py](./snake_game/snake/core/__init__.py)
     * [env_snake.py](./snake_game/snake/core/env_snake.py)
   * [rl/](./snake_game/snake/rl)
     * [__init__.py](./snake_game/snake/rl/__init__.py)
     * [agent_dqn.py](./snake_game/snake/rl/agent_dqn.py)
     * [dqn_model.py](./snake_game/snake/rl/dqn_model.py)
     * [memory.py](./snake_game/snake/rl/memory.py)
     * [train_dqn.py](./snake_game/snake/rl/agent_dqn.py)
   * [scenes/](./snake_game/snake/scenes) 
     * [__init__.py](./snake_game/snake/scenes/__init__.py)
     * [intro.py](./snake_game/snake/scenes/intro.py)
     * [board.py](./snake_game/snake/scenes/board.py)
  * [main.py](./snake_game/main.py)
  * [requirements.txt](./snake_game/requirements.txt)
  * [README.md](./snake_game/README.md)
 ## Cài đặt
  1. Tải mã nguồn
  ```git
  git clone https://github.com/DuongHongDuc-az/Snake-Game.git
  cd snake_game/snake_game
  ```
  2. Cài đặt môi trường
  ```terminal
  pip install -r requirements.txt
  ```
## Cách sử dụng
 1. Chạy trò chơi
 ```terminal
 python main.py
 ```
 2. Huấn luyện agent mói
 ```
 python snake/rl/train_dqn.py
 ```
 ## Công nghệ sử dụng
Ngôn ngữ: Python
Đồ họa, âm thanh: Pygame
Trí tuệ nhân tạo: Pytorch
##  Sinh viên thực hiện
- Trương Lý Nhật Duy

- Dương Hồng Đức

- Nguyễn Gia Huy

- Lý Nguyễn Quốc Dũng

- Ngô Trần Phương Anh
