import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
import requests
import json
from datetime import datetime, timedelta
from PIL import Image, ImageTk
import os
import sys
from pathlib import Path

class WeatherApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Weather Forecast")
        self.root.geometry("1200x800")
        
        # Set transparency
        self.root.attributes('-alpha', 0.95)
        
        # Configure appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # API Configuration
        self.api_key = "Your API Key"
        self.base_url = "http://api.weatherapi.com/v1"
        
        # Settings
        self.settings = {
            "theme": "dark",
            "temp_unit": "celsius",
            "transparency": 0.95,
            "auto_refresh": True,
            "refresh_interval": 30,  # minutes
            "show_notifications": True
        }
        
        # Load icons
        self.load_icons()
        
        # Create main containers
        self.setup_main_layout()
        self.setup_sidebar()
        self.setup_content_area()
        
        # Initialize current view and location
        self.current_view = "forecast"
        self.current_city = "Jaipur, Rajasthan, India"  # Changed default location
        
    def load_icons(self):
        # Define icon paths
        icon_size = 24
        self.icons = {
            "forecast": self.create_icon("🌤️", icon_size),
            "map": self.create_icon("🗺️", icon_size),
            "hourly": self.create_icon("⏱️", icon_size),
            "calendar": self.create_icon("📅", icon_size),
            "settings": self.create_icon("⚙️", icon_size),
            "search": self.create_icon("🔍", icon_size),
            "humidity": self.create_icon("💧", icon_size),
            "wind": self.create_icon("🌪️", icon_size),
            "temperature": self.create_icon("🌡️", icon_size),
            "uv": self.create_icon("☀️", icon_size)
        }
        
    def create_icon(self, emoji, size):
        label = tk.Label(text=emoji, font=("Segoe UI Emoji", size))
        return label.cget("text")
        
    def setup_main_layout(self):
        # Configure main grid
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
    def setup_sidebar(self):
        # Sidebar frame with transparency
        self.sidebar = ctk.CTkFrame(self.root, width=200, corner_radius=10, fg_color=("white", "gray25"))
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.sidebar.grid_rowconfigure(7, weight=1)
        
        # App title with icon
        title_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        title_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        
        ctk.CTkLabel(
            title_frame,
            text="🌈",
            font=ctk.CTkFont(size=24)
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkLabel(
            title_frame,
            text="Weather App",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(side="left")
        
        # Sidebar buttons with icons
        buttons = [
            ("Forecast", "forecast", self.show_forecast),
            ("Maps", "map", self.show_maps),
            ("Hourly", "hourly", self.show_hourly),
            ("Monthly", "calendar", self.show_monthly),
            ("Settings", "settings", self.show_settings)
        ]
        
        for i, (text, icon, command) in enumerate(buttons, start=1):
            btn = ctk.CTkButton(
                self.sidebar,
                text=f" {self.icons[icon]} {text}",
                command=command,
                anchor="w",
                font=ctk.CTkFont(size=14),
                height=40,
                corner_radius=10,
                fg_color="transparent",
                hover_color=("gray75", "gray35")
            )
            btn.grid(row=i, column=0, padx=20, pady=5, sticky="ew")
        
        # Theme switcher
        self.setup_theme_switcher()
        
    def setup_theme_switcher(self):
        theme_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        theme_frame.grid(row=8, column=0, padx=20, pady=(10, 0), sticky="ew")
        
        ctk.CTkLabel(
            theme_frame,
            text="Theme:",
            font=ctk.CTkFont(size=12)
        ).pack(side="left")
        
        self.theme_menu = ctk.CTkOptionMenu(
            theme_frame,
            values=["Dark", "Light", "System"],
            command=self.change_appearance_mode,
            width=100
        )
        self.theme_menu.pack(side="right")
        
    def setup_content_area(self):
        # Main content area with transparency
        self.content = ctk.CTkFrame(
            self.root,
            corner_radius=10,
            fg_color=("white", "gray25")
        )
        self.content.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(1, weight=1)
        
        # Search bar
        self.setup_search_bar()
        
        # Weather display area
        self.weather_frame = ctk.CTkFrame(
            self.content,
            corner_radius=10,
            fg_color=("gray95", "gray20")
        )
        self.weather_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        
    def setup_search_bar(self):
        search_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        search_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 0))
        search_frame.grid_columnconfigure(0, weight=1)
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="🔍 Enter city name...",
            font=ctk.CTkFont(size=14),
            height=40
        )
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        self.search_button = ctk.CTkButton(
            search_frame,
            text="Search",
            width=100,
            height=40,
            command=self.search_city
        )
        self.search_button.grid(row=0, column=1)
        
    def search_city(self):
        city = self.search_entry.get()
        if city:
            self.current_city = city
            self.update_weather_display()
            
    def update_weather_display(self):
        try:
            # Get current weather
            current_url = f"{self.base_url}/current.json"
            forecast_url = f"{self.base_url}/forecast.json"
            
            params = {
                "key": self.api_key,
                "q": self.current_city,
                "days": 7,
                "aqi": "yes"
            }
            
            current_response = requests.get(current_url, params=params)
            forecast_response = requests.get(forecast_url, params=params)
            
            if current_response.status_code == 200 and forecast_response.status_code == 200:
                current_data = current_response.json()
                forecast_data = forecast_response.json()
                self.display_weather(current_data, forecast_data)
            else:
                messagebox.showerror("Error", "Could not fetch weather data")
                
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            
    def display_weather(self, current_data, forecast_data):
        # Clear previous display
        for widget in self.weather_frame.winfo_children():
            widget.destroy()
            
        # Configure grid
        self.weather_frame.grid_columnconfigure(0, weight=1)
        
        # Current weather card
        current_card = ctk.CTkFrame(self.weather_frame)
        current_card.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        # Location and temperature
        location_label = ctk.CTkLabel(
            current_card,
            text=f"{current_data['location']['name']}, {current_data['location']['country']}",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        location_label.pack(pady=(20, 10))
        
        temp_label = ctk.CTkLabel(
            current_card,
            text=f"{current_data['current']['temp_c']}°C",
            font=ctk.CTkFont(size=48, weight="bold")
        )
        temp_label.pack()
        
        condition_label = ctk.CTkLabel(
            current_card,
            text=current_data['current']['condition']['text'],
            font=ctk.CTkFont(size=18)
        )
        condition_label.pack(pady=(0, 20))
        
        # Weather details
        details_frame = ctk.CTkFrame(current_card)
        details_frame.pack(fill="x", padx=40, pady=(0, 20))
        
        details = [
            ("Humidity", f"{current_data['current']['humidity']}%"),
            ("Wind", f"{current_data['current']['wind_kph']} km/h"),
            ("Feels Like", f"{current_data['current']['feelslike_c']}°C"),
            ("UV Index", str(current_data['current']['uv']))
        ]
        
        for i, (label, value) in enumerate(details):
            detail_frame = ctk.CTkFrame(details_frame)
            detail_frame.grid(row=0, column=i, padx=10, sticky="ew")
            
            ctk.CTkLabel(
                detail_frame,
                text=label,
                font=ctk.CTkFont(size=12)
            ).pack()
            
            ctk.CTkLabel(
                detail_frame,
                text=value,
                font=ctk.CTkFont(size=16, weight="bold")
            ).pack()
        
        # Forecast section
        forecast_label = ctk.CTkLabel(
            self.weather_frame,
            text="7-Day Forecast",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        forecast_label.grid(row=1, column=0, sticky="w", padx=20, pady=(0, 10))
        
        # Forecast cards container
        forecast_container = ctk.CTkFrame(self.weather_frame)
        forecast_container.grid(row=2, column=0, sticky="ew")
        
        # Create forecast cards
        for i, day in enumerate(forecast_data['forecast']['forecastday']):
            self.create_forecast_card(forecast_container, day, i)
            
    def create_forecast_card(self, parent, day_data, index):
        card = ctk.CTkFrame(parent)
        card.grid(row=0, column=index, padx=10, pady=10, sticky="nsew")
        
        date = datetime.strptime(day_data['date'], '%Y-%m-%d').strftime('%a')
        
        ctk.CTkLabel(
            card,
            text=date,
            font=ctk.CTkFont(size=14)
        ).pack(pady=5)
        
        ctk.CTkLabel(
            card,
            text=f"{day_data['day']['maxtemp_c']}°C",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack()
        
        ctk.CTkLabel(
            card,
            text=f"{day_data['day']['mintemp_c']}°C",
            font=ctk.CTkFont(size=12)
        ).pack(pady=5)
        
        ctk.CTkLabel(
            card,
            text=day_data['day']['condition']['text'],
            font=ctk.CTkFont(size=12)
        ).pack(pady=(0, 5))
        
    def show_forecast(self):
        self.current_view = "forecast"
        self.update_weather_display()
        
    def show_maps(self):
        # Implement maps view
        pass
        
    def show_hourly(self):
        # Implement hourly forecast view
        pass
        
    def show_monthly(self):
        # Implement monthly forecast view
        pass
        
    def show_settings(self):
        settings_window = ctk.CTkToplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("500x600")
        settings_window.attributes('-alpha', self.settings["transparency"])
        
        # Main settings container
        settings_frame = ctk.CTkFrame(settings_window)
        settings_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Settings title
        ctk.CTkLabel(
            settings_frame,
            text="⚙️ Settings",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(pady=20)
        
        # Appearance settings
        self.create_settings_section(settings_frame, "Appearance", [
            {
                "type": "option",
                "label": "Theme",
                "key": "theme",
                "values": ["Dark", "Light", "System"],
                "command": self.change_appearance_mode
            },
            {
                "type": "slider",
                "label": "Transparency",
                "key": "transparency",
                "from_": 0.5,
                "to": 1.0,
                "command": self.update_transparency
            }
        ])
        
        # Weather settings
        self.create_settings_section(settings_frame, "Weather", [
            {
                "type": "option",
                "label": "Temperature Unit",
                "key": "temp_unit",
                "values": ["Celsius", "Fahrenheit"]
            },
            {
                "type": "switch",
                "label": "Auto Refresh",
                "key": "auto_refresh"
            },
            {
                "type": "option",
                "label": "Refresh Interval",
                "key": "refresh_interval",
                "values": ["15 min", "30 min", "1 hour"]
            }
        ])
        
        # Notification settings
        self.create_settings_section(settings_frame, "Notifications", [
            {
                "type": "switch",
                "label": "Weather Alerts",
                "key": "show_notifications"
            },
            {
                "type": "switch",
                "label": "Severe Weather Warnings",
                "key": "severe_warnings"
            }
        ])
        
    def create_settings_section(self, parent, title, options):
        section = ctk.CTkFrame(parent)
        section.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            section,
            text=title,
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=10, pady=5)
        
        for option in options:
            option_frame = ctk.CTkFrame(section, fg_color="transparent")
            option_frame.pack(fill="x", padx=20, pady=5)
            
            ctk.CTkLabel(
                option_frame,
                text=option["label"],
                font=ctk.CTkFont(size=12)
            ).pack(side="left")
            
            if option["type"] == "option":
                menu = ctk.CTkOptionMenu(
                    option_frame,
                    values=option["values"],
                    width=120,
                    command=option.get("command", None)
                )
                menu.pack(side="right")
                
            elif option["type"] == "switch":
                switch = ctk.CTkSwitch(
                    option_frame,
                    text="",
                    command=option.get("command", None)
                )
                switch.pack(side="right")
                
            elif option["type"] == "slider":
                slider = ctk.CTkSlider(
                    option_frame,
                    from_=option["from_"],
                    to=option["to"],
                    command=option["command"]
                )
                slider.pack(side="right", padx=10)
                
    def update_transparency(self, value):
        self.settings["transparency"] = value
        self.root.attributes('-alpha', value)
        
    def change_appearance_mode(self, new_appearance_mode):
        ctk.set_appearance_mode(new_appearance_mode.lower())
        self.settings["theme"] = new_appearance_mode.lower()
        
    def run(self):
        self.update_weather_display()
        self.root.mainloop()

if __name__ == "__main__":
    app = WeatherApp()
    app.run() 