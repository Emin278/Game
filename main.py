import arcade

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Province Strategy Game with Diplomacy"

MENU = 0
GAME = 1
DIPLOMACY = 2

MONTH_DAYS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

def format_date(turn):
    total_days = turn * 10
    year = 2000
    month = 1
    day = 1
    day += total_days
    while True:
        days_in_month = MONTH_DAYS[month - 1]
        if day > days_in_month:
            day -= days_in_month
            month += 1
            if month > 12:
                month = 1
                year += 1
        else:
            break
    return f"{day:02d}/{month:02d}/{year}"

class Button:
    def __init__(self, x, y, width, height, text):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text

    def draw(self):
        arcade.draw_rectangle_filled(self.x + self.width / 2, self.y + self.height / 2,
                                     self.width, self.height, arcade.color.LIGHT_GRAY)
        arcade.draw_rectangle_outline(self.x + self.width / 2, self.y + self.height / 2,
                                      self.width, self.height, arcade.color.BLACK, 2)
        arcade.draw_text(self.text, self.x + 10, self.y + (self.height / 2) - 10,
                         arcade.color.BLACK, 14)

    def is_clicked(self, mouse_x, mouse_y):
        return (self.x <= mouse_x <= self.x + self.width and
                self.y <= mouse_y <= self.y + self.height)

class Province:
    def __init__(self, x, y, width, height, color, name):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.name = name

    def draw(self):
        arcade.draw_rectangle_filled(self.x + self.width / 2, self.y + self.height / 2,
                                     self.width, self.height, self.color)
        arcade.draw_rectangle_outline(self.x + self.width / 2, self.y + self.height / 2,
                                      self.width, self.height, arcade.color.BLACK, 2)
        arcade.draw_text(self.name, self.x + 10, self.y + self.height / 2 - 10,
                         arcade.color.BLACK, 12)

class Country:
    def __init__(self, name, treasury, population):
        self.name = name
        self.treasury = treasury
        self.population = population
        self.relationships = {}  # {ülke_adı: ilişki puanı}

    def update_relationships(self):
        for other in self.relationships:
            if self.relationships[other] > -100:
                self.relationships[other] += 1  # her tur ilişki +1
                if self.relationships[other] > 100:
                    self.relationships[other] = 100

class GameWindow(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.ASH_GREY)

        self.state = MENU

        # Menü butonları
        self.play_button = Button(350, 300, 200, 60, "Oyna")
        self.exit_button = Button(350, 200, 200, 60, "Çıkış")

        # Hız ayar butonları
        self.speed_up_button = Button(800, 560, 40, 30, "+")
        self.speed_down_button = Button(750, 560, 40, 30, "-")

        self.auto_turn_speed = 3
        self.speed_map = {1: 1.0, 2: 0.7, 3: 0.5, 4: 0.3, 5: 0.2}
        self.turn_time_accumulator = 0.0
        self.turn = 0

        # Basit harita
        self.provinces = [
            Province(50, 400, 120, 80, arcade.color.RED_DEVIL, "İstanbul"),
            Province(200, 400, 120, 80, arcade.color.BLUE, "Ankara"),
            Province(350, 400, 120, 80, arcade.color.GREEN, "İzmir"),
            Province(500, 400, 120, 80, arcade.color.YELLOW, "Antalya"),
            Province(650, 400, 120, 80, arcade.color.ORANGE, "Trabzon"),
        ]

        # Ülkeler
        self.countries = [
            Country("Ülke A", treasury=1000, population=5000),
            Country("Ülke B", treasury=1500, population=6000),
            Country("Ülke C", treasury=800, population=4000),
            Country("Ülke D", treasury=1200, population=5500),
            Country("Ülke E", treasury=1100, population=5300),
        ]

        # İlişkileri başlat
        for c in self.countries:
            c.relationships = {other.name: 10 for other in self.countries if other != c}

        # Diplomasi menüsü için
        self.diplomacy_buttons = [
            Button(700, 380, 180, 40, "Savaş İlan Et"),
            Button(700, 320, 180, 40, "İlişki +1"),
            Button(700, 260, 180, 40, "İlişki -5"),
            Button(700, 200, 180, 40, "Hakaret (-30)")
        ]

        self.selected_diplomacy_country = None

    def on_draw(self):
        arcade.start_render()

        if self.state == MENU:
            self.draw_menu()
        elif self.state == GAME:
            self.draw_game()
        elif self.state == DIPLOMACY:
            self.draw_game()
            self.draw_diplomacy()

    def draw_menu(self):
        arcade.draw_text("Ana Menü", SCREEN_WIDTH / 2 - 70, SCREEN_HEIGHT - 150, arcade.color.BLACK, 40)
        self.play_button.draw()
        self.exit_button.draw()

    def draw_game(self):
        # Harita solda
        for prov in self.provinces:
            prov.draw()

        # Tur ve tarih solda üst
        arcade.draw_text(f"Tur: {self.turn}", 50, 550, arcade.color.BLACK, 18)
        arcade.draw_text(f"Tarih: {format_date(self.turn)}", 50, 520, arcade.color.BLACK, 18)

        # Hız ayar butonları sağ üstte
        arcade.draw_text(f"Hız: {self.auto_turn_speed}", 750, 520, arcade.color.BLACK, 18)
        self.speed_up_button.draw()
        self.speed_down_button.draw()

        # Diplomasi menüsüne geçmek için buton (sağ alt)
        arcade.draw_rectangle_filled(750, 50, 130, 50, arcade.color.LIGHT_GRAY)
        arcade.draw_rectangle_outline(750, 50, 130, 50, arcade.color.BLACK, 2)
        arcade.draw_text("Diplomasi Menüsü", 690, 40, arcade.color.BLACK, 14)

    def draw_diplomacy(self):
        # Diplomasi paneli sağ tarafta
        arcade.draw_rectangle_filled(750, 350, 280, 450, arcade.color.LIGHT_GRAY)
        arcade.draw_rectangle_outline(750, 350, 280, 450, arcade.color.BLACK, 3)

        arcade.draw_text("Diplomasi Menüsü", 690, 680, arcade.color.BLACK, 20)

        # Ülke listesi (solda, kutucuklar halinde)
        base_y = 650
        box_height = 35
        for i, country in enumerate(self.countries):
            color = arcade.color.LIGHT_BLUE if self.selected_diplomacy_country == country else arcade.color.WHITE
            arcade.draw_rectangle_filled(100, base_y - i * (box_height + 5), 150, box_height, color)
            arcade.draw_rectangle_outline(100, base_y - i * (box_height + 5), 150, box_height, arcade.color.BLACK, 2)
            arcade.draw_text(country.name, 30, base_y - i * (box_height + 5) - 10, arcade.color.BLACK, 14)

        # Seçilen ülke bilgileri diplomasi panelinde
        if self.selected_diplomacy_country:
            c = self.selected_diplomacy_country
            arcade.draw_text(f"Ülke: {c.name}", 650, 600, arcade.color.BLACK, 16)
            arcade.draw_text(f"Hazine: {c.treasury}", 650, 570, arcade.color.BLACK, 16)
            arcade.draw_text(f"Nüfus: {c.population}", 650, 540, arcade.color.BLACK, 16)

            # İlişki durumu
            player_country = self.countries[0]  # Oyuncu ülke 0
            relation = player_country.relationships.get(c.name, 0)
            arcade.draw_text(f"İlişki: {relation}", 650, 510, arcade.color.BLACK, 16)

            # Diplomasi butonları
            for btn in self.diplomacy_buttons:
                btn.draw()

    def on_update(self, delta_time):
        if self.state in (GAME, DIPLOMACY):
            self.turn_time_accumulator += delta_time
            duration = self.speed_map[self.auto_turn_speed]
            if self.turn_time_accumulator >= duration:
                self.turn += 1
                self.turn_time_accumulator = 0
                for country in self.countries:
                    country.update_relationships()

    def on_mouse_press(self, x, y, button, modifiers):
        if self.state == MENU:
            if self.play_button.is_clicked(x, y):
                self.state = GAME
            elif self.exit_button.is_clicked(x, y):
                arcade.close_window()
        elif self.state == GAME:
            if self.speed_up_button.is_clicked(x, y):
                if self.auto_turn_speed < 5:
                    self.auto_turn_speed += 1
            elif self.speed_down_button.is_clicked(x, y):
                if self.auto_turn_speed > 1:
                    self.auto_turn_speed -= 1
            else:
                # Diplomasi menüsüne geçmek için butona tıklama kontrolü
                # Diplomasi butonu koordinatları:
                # Merkez (750,50), boyut (130,50)
                if (685 <= x <= 815) and (25 <= y <= 75):
                    self.state = DIPLOMACY
        elif self.state == DIPLOMACY:
            # Ülke seçimi sol taraftan
            base_y = 650
            box_height = 35
            for i, country in enumerate(self.countries):
                box_x = 100
                box_y = base_y - i * (box_height + 5)
                if (box_x - 75 <= x <= box_x + 75) and (box_y - box_height / 2 <= y <= box_y + box_height / 2):
                    if country != self.countries[0]:  # Kendi ülkesini seçme
                        self.selected_diplomacy_country = country
                    return

            # Diplomasi butonları tıklaması
            if self.selected_diplomacy_country:
                for btn in self.diplomacy_buttons:
                    if btn.is_clicked(x, y):
                        self.apply_diplomacy_action(btn.text)
                        break

            # Diplomasi menüsünden çıkmak için ekranın sol tarafına tıklayınca oyun ekranına dön
            if x < 600:
                self.state = GAME
                self.selected_diplomacy_country = None

    def apply_diplomacy_action(self, action):
        player_country = self.countries[0]
        target = self.selected_diplomacy_country
        if not target or target == player_country:
            return

        if action == "Savaş İlan Et":
            player_country.relationships[target.name] = -100
            target.relationships[player_country.name] = -100
        elif action == "İlişki +1":
            player_country.relationships[target.name] = min(100, player_country.relationships[target.name] + 1)
            target.relationships[player_country.name] = min(100, target.relationships[player.name] + 1)
        elif action == "İlişki -5":
            player_country.relationships[target.name] = max(-100, player_country.relationships[target.name] - 5)
            target.relationships[player_country.name] = max(-100, target.relationships[player.name] - 5)
        elif action == "Hakaret (-30)":
            player_country.relationships[target.name] = max(-100, player_country.relationships[target.name] - 30)
            target.relationships[player_country.name] = max(-100, target.relationships[player.name] - 30)

def main():
    window = GameWindow()
    arcade.run()

if __name__ == "__main__":
    main()
