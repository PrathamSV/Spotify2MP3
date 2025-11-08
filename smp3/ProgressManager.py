import sys


class ProgressManager:

    def __init__(self, tracks):
        self.name_list = []
        for track in tracks.values():
            self.name_list.append(track.name)

        self.max_count = len(self.name_list)

        self.count = 0
        self.fill_char = "█"
        self.empty_char = ' '
        self.cap_char = '|'
        self.width = 50

        self.error_list = []
        self.prev_length = 0

    def __progress_bar2(self, msg, update_count: bool) -> None:

        if msg is not None:
            msg = " - " + msg  # for formatting

        fill_amount = int(self.count / self.max_count * self.width)
        fill_percentage = int(self.count / self.max_count * 100)
        fraction_completed = str(self.count) + '/' + str(self.max_count)

        fill_str = self.fill_char * fill_amount
        empty_str = self.empty_char * (self.width - fill_amount)

        out = f"{self.cap_char}{fill_str}{empty_str}{self.cap_char} {str(fill_percentage)}% [{fraction_completed}]{msg}"

        print(' ' * self.prev_length, end='\r')

        print(out, end='\r')
        sys.stdout.flush()

        self.prev_length = len(out)

        if update_count:
            self.count += 1


    def __progress_bar(self, msg, update_count: bool) -> None:

        simple_bar(max_count=self.max_count, count=self.count, msg=msg)

        if update_count:
            self.count += 1

    def downloaded(self):
        msg = f"Song {self.name_list[self.count]} downloaded"
        self.__progress_bar(msg, False)

    def downloading(self):
        msg = f"Downloading: {self.name_list[self.count]}"
        self.__progress_bar(msg, False)

    def converting(self):
        msg = f"Converting: {self.name_list[self.count]}"
        self.__progress_bar(msg, False)

    def searching(self):
        msg = f"Searching for: {self.name_list[self.count]}"
        self.__progress_bar(msg, False)

    def added_metadata(self):
        msg = f"Added metadata for: {self.name_list[self.count]}"
        self.__progress_bar(msg, True)

    def error(self):
        msg = f"ERROR: Could not download {self.name_list[self.count]}"
        self.error_list.append(self.song_list[self.index])
        self.__progress_bar(msg, True)

    def completed(self):
        msg = 'Completed'
        self.__progress_bar(msg, False)
        print(' ' * self.prev_length, end='\r')
        sys.stdout.flush()
        return self.error_list


def simple_bar(count: int, max_count: int, msg: str = None, fill_char: str = "█", empty_char: str = ' ',
               lcap_char: str = '|', rcap_char: str = '|', width: int = 50) -> int:
    """A progress bar...

    :param int count: Amount progressed
    :param int max_count: Maximum amount able to be progressed
    :param str msg: Message to display
    :param str fill_char: Character to fill up progress bar
    :param str empty_char: Character to fill up empty space in progress bar
    :param str lcap_char: Character to cap the left of the progress bar
    :param str rcap_char: Character to cap the right of the progress bar
    :param int width: Width of progress bar
    """

    if hasattr(simple_bar, 'prev_length'):
        prev = getattr(simple_bar, 'prev_length')
    else:
        prev = 0

    if msg is not None:
        msg = " - " + msg  # for formatting

    fill_amount = int(count / max_count * width)
    fill_percentage = int(count / max_count * 100)
    fraction_completed = str(count) + '/' + str(max_count)

    fill_str = fill_char * fill_amount
    empty_str = empty_char * (width - fill_amount)

    print(' ' * prev, end='\r')

    out = f"{lcap_char}{fill_str}{empty_str}{rcap_char} {str(fill_percentage)}% [{fraction_completed}]{msg}"
    print(out, end='\r')

    sys.stdout.flush()

    setattr(simple_bar, 'prev_length', len(out))

    return len(out)
