# Copyright 2024 Superlinked, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from beartype.typing import Callable

DEFAULT_CHUNK_SIZE: int = 250
DEFAULT_CHUNK_OVERLAP: int = 20
DEFAULT_REMOVE_SPLIT_CHARS: list[str] = ["\n"]
DEFAULT_ADDITIONAL_SPLIT_CHARS: list[str] = [".", "!", "?"]


class Chunker:
    @staticmethod
    def _split_text_keep_sep(text: str, separator: str, keep_sep: bool = True) -> list[str]:
        """Split text with separator and keep the separator at the end of each split."""
        parts = text.split(separator)
        result = [
            part + f"{separator} " * (i < len(parts) - 1) * keep_sep
            for i, part in enumerate(text.split(separator))
            if part
        ]
        return result

    def _split_by_sep(self, sep: str, keep_sep: bool = True) -> Callable[[str], list[str]]:
        """Split text by separator."""
        return lambda text: self._split_text_keep_sep(text, sep, keep_sep)

    def _split(
        self,
        text: str,
        chunk_size: int,
        remove_splitter_chars: list[str] | None = None,
        additional_splitter_chars: list[str] | None = None,
    ) -> list[str]:
        """
        Break text into logical splits that are smaller than chunk size.
        NOTE: the splits
            - do not contain the separators if separator in remove_splitter_chars
            - contain the separators if separator in additional_splitter_chars.
        """
        if remove_splitter_chars is None:
            remove_splitter_chars = DEFAULT_REMOVE_SPLIT_CHARS
        if additional_splitter_chars is None:
            additional_splitter_chars = DEFAULT_ADDITIONAL_SPLIT_CHARS
        splits_to_process: list[str] = [text]
        new_splits: list[str] = []
        split_fns: list[Callable[[str], list[str]]] = [
            self._split_by_sep(sep, keep_sep=False) for sep in remove_splitter_chars
        ] + [self._split_by_sep(sep, keep_sep=True) for sep in additional_splitter_chars + [" "]]

        while len(splits_to_process) > 0:
            current_split: str = splits_to_process.pop(0)
            if len(current_split) <= chunk_size:
                new_splits.append(current_split)
            else:
                sub_split: list[str] = next(
                    (
                        sub_split
                        for sub_split in [split_fn(" ".join(current_split.split())) for split_fn in split_fns]
                        if len(sub_split) > 1
                    ),
                    [],
                )
                if sub_split:
                    splits_to_process = sub_split + splits_to_process
                else:
                    new_splits.append(current_split)

        return new_splits

    def _merge(self, splits: list[str], chunk_size: int, chunk_overlap: int) -> list[str]:
        """Merge splits into chunks.

        The high-level idea is to keep adding splits to a chunk until we
        exceed the chunk size, then we start a new chunk with overlap.

        When we start a new chunk, we pop off the first element of the previous
        chunk until the total length is less than the chunk size.
        """
        chunks: list[str] = []

        cur_chunk: list[str] = []
        cur_len = 0
        for split in splits:
            split_len = len(split)
            # if we exceed the chunk size after adding the new split, then
            # we need to end the current chunk and start a new one
            if cur_len + split_len > chunk_size:
                # end the previous chunk
                chunk = "".join(cur_chunk).strip()
                if chunk:
                    chunks.append(chunk)

                # start a new chunk with overlap
                # keep popping off the first element of the previous chunk until:
                #   1. the current chunk length is less than chunk overlap
                #   2. the total length is less than chunk size
                while cur_len > chunk_overlap or cur_len + split_len > chunk_size:
                    # pop off the first element
                    first_chunk = cur_chunk.pop(0)
                    cur_len -= len(first_chunk)

            cur_chunk.append(split)
            cur_len += split_len

        # handle the last chunk
        chunk = "".join(cur_chunk).strip()
        if chunk:
            chunks.append(chunk)

        return [" ".join(chunk.split()) for chunk in chunks]

    def chunk_text(
        self,
        text: str,
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
        split_chars_keep: list[str] | None = None,
        split_chars_remove: list[str] | None = None,
    ) -> list[str]:
        if not text:
            return []
        chunk_size = DEFAULT_CHUNK_SIZE if chunk_size is None else chunk_size
        chunk_overlap = DEFAULT_CHUNK_OVERLAP if chunk_overlap is None else chunk_overlap
        splits = self._split(
            text=text,
            chunk_size=chunk_size,
            remove_splitter_chars=split_chars_keep,
            additional_splitter_chars=split_chars_remove,
        )
        return self._merge(splits=splits, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
