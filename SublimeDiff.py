import os
import glob
import subprocess
import tempfile
import sublime
import sublime_plugin
from typing import Tuple
from io import TextIOWrapper

SUBLIME_DIFF_TMP_PREFIX: str = "SublimeDiff-"

class SublimeDiffCleanCommand(sublime_plugin.ApplicationCommand):

  @staticmethod
  def _attempt_remove_tmp_files() -> int:
    tmp_files = glob.glob(f"{tempfile.gettempdir()}/{SUBLIME_DIFF_TMP_PREFIX}*")
    for f in tmp_files:
      os.remove(f)
    return len(tmp_files)

  def run(self):
    files_removed_count = self._attempt_remove_tmp_files()
    if files_removed_count > 0:
      message = f"SublimeDiff: {files_removed_count} files removed."
    else:
      message = "SublimeDiff: No tmp files found."
    sublime.status_message(message)

class SublimeDiffCommand(sublime_plugin.WindowCommand):

  @staticmethod
  def _get_or_create_tmp_file(view: sublime.View, tmp_name: str, f: TextIOWrapper) -> str:
    # file_name_on_disk = view.file_name()
    # if not file_name_on_disk:
    content = view.substr(sublime.Region(0, view.size()))
    f.write(content)
    f.flush()
    return tmp_name
    # else:
    #   return file_name_on_disk

  @staticmethod
  def _diff_files(left_file: str, right_file: str) -> None:
    command = ["smerge", "mergetool", "--no-wait", left_file, left_file, right_file]
    subprocess.Popen(command)
    # process = subprocess.run(command, capture_output=True, text=True)
    # if process.returncode != 0 and process.stderr:
    #     sublime.error_message(f'Error running process: {process.stderr}')

  def run(self):
    # settings = sublime.load_settings("explore.sublime-settings")
    if self.window.num_groups() == 1:
      self.window.set_layout({
        "cols": [0.0, 0.5, 1.0],
        "rows": [0.0, 1.0],
        "cells": [[0, 0, 1, 1], [1, 0, 2, 1]]
      })
      self.window.focus_group(1)
      self.window.new_file()
      # XXX - should add some instructions here to the empty view
      # active_view = self.window.active_view()
      # if active_view:
      #   active_view.add_anno('sublime_diff', sublime.Region(0), "Insert", sublime.LAYOUT_INLINE)

    elif self.window.num_groups() == 2:
      left_active_view = self.window.active_view_in_group(0)
      right_active_view = self.window.active_view_in_group(1)
      if left_active_view and right_active_view:
        left_tmp = tempfile.NamedTemporaryFile(prefix=SUBLIME_DIFF_TMP_PREFIX, delete = False)
        right_tmp = tempfile.NamedTemporaryFile(prefix=SUBLIME_DIFF_TMP_PREFIX, delete = False)

        with open(left_tmp.name, "w") as left_f, open(right_tmp.name, "w") as right_f:
          left_file = self._get_or_create_tmp_file(left_active_view, left_tmp.name, left_f)
          right_file = self._get_or_create_tmp_file(right_active_view, right_tmp.name, right_f)
          self._diff_files(left_file, right_file)

      else:
        pass
    else:
      # do nothing at all
      sublime.status_message("More than two groups is not supported.")
      pass

