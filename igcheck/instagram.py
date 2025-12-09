"""Instagram API wrapper using instagrapi."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from instagrapi import Client
from instagrapi.exceptions import (
    BadPassword,
    ChallengeRequired,
    LoginRequired,
    TwoFactorRequired,
)


@dataclass
class UserInfo:
    """Represents an Instagram user."""

    user_id: str
    username: str
    full_name: str
    profile_url: str


class InstagramClient:
    """Wrapper around instagrapi Client for fetching followers/following."""

    SESSION_FILE = "session.json"

    def __init__(self, session_path: Path | None = None):
        self.client = Client()
        self.session_path = session_path or Path(self.SESSION_FILE)
        self._user_id: str | None = None

    def login(
        self,
        username: str,
        password: str,
        verification_code_callback: Callable[[], str] | None = None,
    ) -> None:
        """
        Login to Instagram with session persistence.

        Args:
            username: Instagram username
            password: Instagram password
            verification_code_callback: Optional callback to get 2FA code from user
        """
        if self.session_path.exists():
            self.client.load_settings(self.session_path)

        try:
            self.client.login(username, password)
            self._user_id = str(self.client.user_id)
            self.client.dump_settings(self.session_path)
        except TwoFactorRequired:
            if verification_code_callback is None:
                raise RuntimeError("Two-factor authentication required but no callback provided")
            code = verification_code_callback()
            self.client.two_factor_login(code)
            self._user_id = str(self.client.user_id)
            self.client.dump_settings(self.session_path)
        except ChallengeRequired:
            raise RuntimeError(
                "Instagram challenge required. "
                "Please log in via the Instagram app to verify your account, then try again."
            )
        except BadPassword:
            raise RuntimeError("Invalid password. Please check your credentials.")
        except LoginRequired:
            raise RuntimeError("Login failed. Please check your credentials and try again.")

    @property
    def user_id(self) -> str:
        """Get the logged-in user's ID."""
        if self._user_id is None:
            raise RuntimeError("Not logged in. Call login() first.")
        return self._user_id

    def get_followers(self) -> dict[str, UserInfo]:
        """
        Get all followers of the logged-in user.

        Returns:
            Dictionary mapping user_id to UserInfo
        """
        followers_data = self.client.user_followers(self.user_id)
        return self._convert_users(followers_data)

    def get_following(self) -> dict[str, UserInfo]:
        """
        Get all accounts the logged-in user follows.

        Returns:
            Dictionary mapping user_id to UserInfo
        """
        following_data = self.client.user_following(self.user_id)
        return self._convert_users(following_data)

    def _convert_users(self, users_data: dict) -> dict[str, UserInfo]:
        """Convert instagrapi user data to UserInfo objects."""
        result = {}
        for user_id, user in users_data.items():
            result[str(user_id)] = UserInfo(
                user_id=str(user_id),
                username=user.username,
                full_name=user.full_name or "",
                profile_url=f"https://instagram.com/{user.username}",
            )
        return result

    def get_non_followers(self) -> list[UserInfo]:
        """
        Find accounts you follow that don't follow you back.

        Returns:
            List of UserInfo for accounts that don't follow back
        """
        followers = self.get_followers()
        following = self.get_following()

        follower_ids = set(followers.keys())
        following_ids = set(following.keys())

        non_follower_ids = following_ids - follower_ids

        return [following[uid] for uid in non_follower_ids]

    def unfollow_user(self, user_id: str) -> bool:
        """
        Unfollow a user by their user ID.

        Args:
            user_id: The Instagram user ID to unfollow

        Returns:
            True if successful, False otherwise
        """
        return self.client.user_unfollow(user_id)
