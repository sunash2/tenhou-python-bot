# -*- coding: utf-8 -*-
from mahjong.constants import EAST
from mahjong.tile import TilesConverter

from game.ai.first_version.defence.defence import Defence, DefenceTile


class PossibleFormsAnalyzer(object):
    POSSIBLE_TANKI = 1
    POSSIBLE_SYANPON = 2
    POSSIBLE_PENCHAN = 3
    POSSIBLE_KANCHAN = 4
    POSSIBLE_RYANMEN = 5

    defence = None

    def __init__(self, defence):
        self.defence = defence

    def _init_zero_forms_count(self):
        forms_count = dict()

        forms_count[self.POSSIBLE_TANKI] = 0
        forms_count[self.POSSIBLE_SYANPON] = 0
        forms_count[self.POSSIBLE_PENCHAN] = 0
        forms_count[self.POSSIBLE_KANCHAN] = 0
        forms_count[self.POSSIBLE_RYANMEN] = 0

        return forms_count

    def calculate_possible_forms(self, safe_tiles):
        possible_forms_34 = [None] * 34

        closed_hand_34 = TilesConverter.to_34_array(self.defence.player.closed_hand)

        # first of all let's find suji for suits tiles
        suits = self.defence.suits_tiles(closed_hand_34)
        for x in range(0, 3):
            suit = suits[x]

            for y in range(0, 9):
                tile_34_index = y + x * 9

                # we are only interested in tiles that we can discard
                if closed_hand_34[tile_34_index] == 0:
                    continue

                forms_count = self._init_zero_forms_count()
                possible_forms_34[tile_34_index] = forms_count

                # that means there are no possible forms for him to wait (we don't consider furiten here,
                # because we are defending from enemy taking ron)
                if tile_34_index in safe_tiles:
                    continue

                # tanki
                forms_count[self.POSSIBLE_TANKI] = 4 - suit[y]
                # syanpon
                forms_count[self.POSSIBLE_SYANPON] = 3 - suit[y] if suit[y] < 3 else 0
                # penchan
                if y == 2:
                    forms_count[self.POSSIBLE_PENCHAN] = (4 - suit[0]) * (4 - suit[1])
                elif y == 6:
                    forms_count[self.POSSIBLE_PENCHAN] = (4 - suit[8]) * (4 - suit[7])
                # kanchan
                if 1 <= y <= 7:
                    tiles_cnt_left = (4 - suit[y - 1])
                    tiles_cnt_right = (4 - suit[y + 1])
                    forms_count[self.POSSIBLE_KANCHAN] = tiles_cnt_left * tiles_cnt_right

                # ryanmen
                if 0 <= y <= 2:
                    if not (tile_34_index + 3) in safe_tiles:
                        forms_count[self.POSSIBLE_RYANMEN] = (4 - suit[y + 1]) * (4 - suit[y + 2])
                elif 3 <= y <= 5:
                    if not (tile_34_index - 3) in safe_tiles:
                        forms_count[self.POSSIBLE_RYANMEN] += (4 - suit[y - 1]) * (4 - suit[y - 2])
                    if not (tile_34_index + 3) in safe_tiles:
                        forms_count[self.POSSIBLE_RYANMEN] += (4 - suit[y + 1]) * (4 - suit[y + 2])
                else:
                    if not (tile_34_index - 3) in safe_tiles:
                        forms_count[self.POSSIBLE_RYANMEN] = (4 - suit[y - 1]) * (4 - suit[y - 2])

        for tile_34_index in range(EAST, 34):
            if closed_hand_34[tile_34_index] == 0:
                continue

            forms_count = self._init_zero_forms_count()
            possible_forms_34[tile_34_index] = forms_count

            total_tiles = self.defence.player.total_tiles(x, closed_hand_34)

            # tanki
            forms_count[self.POSSIBLE_TANKI] = 4 - total_tiles
            # syanpon
            forms_count[self.POSSIBLE_SYANPON] = 3 - total_tiles if total_tiles < 3 else 0

        return possible_forms_34

    @staticmethod
    def calculate_possible_forms_total(forms_count):
        total = 0

        total += forms_count[PossibleFormsAnalyzer.POSSIBLE_TANKI]
        total += forms_count[PossibleFormsAnalyzer.POSSIBLE_SYANPON]
        total += forms_count[PossibleFormsAnalyzer.POSSIBLE_PENCHAN]
        total += forms_count[PossibleFormsAnalyzer.POSSIBLE_KANCHAN]
        total += forms_count[PossibleFormsAnalyzer.POSSIBLE_RYANMEN]

        return total

    @staticmethod
    def calculate_possible_forms_danger(forms_count):
        danger = 0

        danger += forms_count[PossibleFormsAnalyzer.POSSIBLE_TANKI] * Defence.TileDanger.DANGER_FORM_BONUS_OTHER
        danger += forms_count[PossibleFormsAnalyzer.POSSIBLE_SYANPON] * Defence.TileDanger.DANGER_FORM_BONUS_OTHER
        danger += forms_count[PossibleFormsAnalyzer.POSSIBLE_PENCHAN] * Defence.TileDanger.DANGER_FORM_BONUS_OTHER
        danger += forms_count[PossibleFormsAnalyzer.POSSIBLE_KANCHAN] * Defence.TileDanger.DANGER_FORM_BONUS_OTHER
        danger += forms_count[PossibleFormsAnalyzer.POSSIBLE_RYANMEN] * Defence.TileDanger.DANGER_FORM_BONUS_RYANMEN

        return danger