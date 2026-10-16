#!/bin/bash
# macOS / Bash 3.2. Source patch only; no services or financial operations.
set -euo pipefail
umask 077
ROOT="${PORQUINHO_ROOT:-$HOME/Desktop/Bridge_Companion/porquinho_v33_web_foundation-2}"
PYTHON_BIN="python3"
if [ -x "$ROOT/.venv/bin/python" ]; then PYTHON_BIN="$ROOT/.venv/bin/python"; fi
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
 printf 'FAIL_CLOSED: Python 3.10+ não encontrado; nenhum arquivo alterado.\n'; exit 1
fi
"$PYTHON_BIN" -I -B - "$ROOT" <<'A24_PYTHON'
import sys
if sys.version_info < (3,10):
 raise SystemExit('FAIL_CLOSED: Python 3.10+ necessário; nenhum arquivo alterado.')
from pathlib import Path
import base64,hashlib,io,json,os,shutil,stat,subprocess,tempfile,zipfile
from datetime import datetime
PAYLOAD = "UEsDBBQAAAAIALY1UF0C+kx8xQkAAPQXAAAyAAAAdW5pdmVyc2FsX3BvcnRmb2xpby9nbG9iYWxfbWFya2V0X21pZ3JhdGlvbl9hMjQucHm9WG1z27gR/q5fQbsfQDYM7aS59CoPb0Yn8RzNyZJPkp2krocDkZCFmAJkApTtc/PfuwuAlGTHTq/T1h8svC729dld7u/vD6RSBVPK48tlpemsYN6SltdMv3YTflVSzaWIvKH0KsH1Ac+Z0Fzfe1zMWclExjxZerqkXHBxFe3v77f4ciVL7WVqHc4zoYtwQdWi4LOQy/CLkiKUKlSLSvMi1Gy5mvOCtealXHo5y/iSFp4j0LPTsC/WtOD5aMUsM/bwimokWh8+handiNjdquAZ16mVJZ1xkQNvKqVv39XHC5kB5YwKKTiMWpPuh+SkExPYvKm4WMjoqpAzWrx2+mg08RqIHLyJDklrMjobd5OY5FTTA/w3o4oduDdzyov7CFQA56ajcX1shno6sKRr9hrShkHSygoKFjmpV5OylKV/TouKmWHQXsF+q5WzuacW1C/pbdAuma5K4TlFR7D+9of3ZitasLucXzGl/cDcWdFSMXurBXa7h/9eyWjOyhjYjezQ5zKa6BK01h/h2QhMI3Pmk0rPX//4WvErEoSC3RZcsJjAWMHhTMfTsmLB0cLQULFgd9q3BAN4hc+9gglfMe27E0GwF+NSPUVXElJ7DwREZJqEqDVGvkZcqWq2fbENilTssZbI2bD/21mSfkg6vWQ8STuTSTJNe51pko6T387646RHkJNS3qq44OoRd1Tc+8hO+ZitOfBVgsebi8+9PR59TD/2e9MP6Ul/ctKZdj+kw1GKq73x6PS0ftpZypIOkWDLY3cZW2nPPwNnBDUbgiFaw44mWq762nl/4FGFF57hojs5T/vD886g38PnT/rH4860PxoSkAKjA25a3xHVcgaGXqNjhSupuOZrFv9CC8XQM0AdZsvjCmJfmCg3CzHYu/Y3ApJO+sNj0niSiF3UWsJbEhPDE0HCAuyZzgEwNPNBHJF7vvjpEHdqPjwGbHjip/gwsEPiZCIbZT2GhXA7RupHm2vW90v5hWW69v5tI8SbuDiSlY4vLo8yWQmt4oevLeMAgCLsLjRiKfQFBhrEp+ES3A/fIEVPlVmcQyT4v/NV7T/uThAcLZmmiAPxw3UbTkZX4NHXxuuNivGVayTtEy4gooC+0CnPIQ6A8zVAb7k1tBs3ldQszaoSsfgeFmqATpWsyoylJZuTAETwbuL6+YvHt1DW5apgmsW0KPz6XGQZ9wNrJNxax/E6wmBf+TYs1sjvMxduwM5UZZz7W/NiBaC1mVcrsJ+PfrJkVFUlswo3tOecFXkoixzfuPBBcp4xowH4TVlVAvD4ZC0LUBQs20Gz7uA1oyvY20zs/iUay8vwhojNO+h+tU3MQmCgCK2BxgkB5awryt2z8vmTOMNnbNzUF+yjAdKww93Df/I6wkMm610IQMHWrPQYmh0TrvFGrUxCDmGZCbCNhAwH+57UCzjbWARJ4rn4xj5ozWzU76R34u8wUdviwuxdxg/EyEDaFi4e+0/bcEKcx1m6pG1/Q2LihGep0lRXirR3kMc8AJhibRuE+PqTP4L0m/sk+XQ66Hf7gOxJd9Cx+JbadJyeDTvTaTKZJhZq8KJDkLPheTLu/9JPeukgOe50P6ejMUBld3RyOkggQ3RHw2nyaUrQ++xT8eYlt/nMKztqbXTnZLq8eKSYy0bc584/0hhecOhpRTkdJ5NkfA6SnA1hOBrgcDiapiejXjKAXNfpfQak9CyCXVgyl7GdGie0S+Fh8OoNnAPAiygEosj9B6KyBVtS0rYlUWNVADnSthhYL9lod06hQpu004LOWEEQ3y5cGr8MiYTsXa4NTqcmp9t9M7x8bPQGw0i79mOIYKcmXLMj4MN5hJOG0EovZGkuElRRZwxJeDQcfAYEqEvU1B36neWkbdJdSJo6MF1VM6gdLZ9PDn4FmDLwTUj0RXLhN/cwBQSvyD8EsbWCvEU4ALUGEQQIVk5w9VHqN5UG1hOhtUuIpG2ewqoknVUiLzC5SB3aMSC+S80GbxQmCQqA4DfbWIeZfILEN5f24vfvcBULnKwGK3L45u1f3v3w/q8//o3OMnjW8p7h3tZ73y4zfj4b9gZJCkVGnWEDzJIFlpGmtrZ8m9r3FTkgrzYUW9BjCD6HijTGbiAqJM2V//IlmNWXIrxEgsjq6F6bdNMC6fgVF7T4zuswq0+a6nyXzlEJZW6Zq3+DyMafleGoeERqU10Y69Y2ht4EChCWx3UpUnMTGLvWQu7Fz8Yh9j2waHCoWbQFPwQC5NaG4mYXfJi00SW29iwYQfDUfBJwxtSwidCNPLv4sovKraqdYFY7T9fSBS+HIs2wxktLoMYhYatbrkHWPx6O6NKNUfbiHeFxz1lzL675Mr3Oi/4MKH887k9NbsDS/aRzegoF7raXuzCuTRVebHsx9EO2LsKR6RgsD5GCnlTjIvjGpY1y2/jZCMe4xt8Y+1i7Au6kZLFm/k5vZU2646DGFYIGF+wJ6IKhv4HH6lL4oUFL4pIYJgyTSYZT8rJ7LWXOIVFvLPSM6b4aJhwD+JwfwI/xv5/ev/vzm8O39t8zoOL4mvT/nqSD/gmk3d0OBlREb2NHfiduvxlrBqq3S/6jxlniunPeAqP/LOI20Ps02vCB/02goWj/pyCDlMfBibUs75/AYnDU7EXLaxj70EUxbJrQWUPjgqm8tq7bwo8u19+C1s1nJjxBgqN5HksVSShIMC9chzAZpR/HKNk/zbgLJc40PJTvDw+BLoi28GB9npsrc7DFLTF98oKidTDszZeoaI7kfLtqP05Fg1H31zT5BKKgE3wnd0GCqBSgN55tIsx+PMDQs7umtQCLXjEbzfVHLlQRjv0V9GT8LiYYIldYkpAQdBc3usR85tUdtW2FBF2ycCbze9cK7SSx0DiaT76RlELrKdgNbafPcKt0qXds/bIpWFyP5Dn1omaNUAeGF3I3IyEuYsKny1lOvVU4L+iVatemc3NnJmMPgDJGl237E92W+AUApQJcs0vzolILCGi0proXmV+vg/6E9K1mtkBmGwX2YtDDy9DS/dAZHkOt3DsbI6o32IJAA40AQA6xL8D74MggqJU5RIObnTlqvXCWQT5wewO29rtmVC6BbXcXr0H7ZgA0rAuMFyq81n9BPpfOxsm00x+63qDTnfbPO9NkO4ltJYXkU38y3VVK3S+ZHsf6tmtAjgejnzsDyI7jXxNsjk4/u2vwVnMrJI1QOzi5BX+1Xi62Fi+fg8NNl1BDrVFMCuGEfo+QZWCHgIGwXVEpxLlrur5x6rncpgRdqYXU6ulWwWhpeghZ4ibo4smZLSYX4BMQzWnJTEtUfD9/bnUpJbuBnkpvbaHniYzjh+NKG9v/cSz/F1BLAwQUAAAACAC2NVBdCrAxq2UBAABYAgAAIgAAAHRvb2xzL21pZ3JhdGVfZ2xvYmFsX21hcmtldF9hMjQucHltUU1r5DAMvedXmFySQMZ0y55afOilt9JSeivFaGJlRq1jG9kpzL9feTKzuyx7k8TT+5Datn2iA0NBVY6oFuAvLKrA3ssgKlDfyDQTulpkikGqg4978IoxI/B0VFNMJ922bUNLilwU8CEBZxw/cwxjPuVm5rioBOXoaa8uqBdpm9fn5zdTq97amTxaO2jhjf4b+0ELC4aS3398NDSrXLiv+EGFWBQFJcy6kt5dC00hI5f+ZvyNHTbtNVD1D95W7Tl6inqLYbfIdjlfQQJauP159bgNcWQEZ/drcB6rE2sDLOLVmM7KPgVru7tGJXNNrh/4sC7i/aV23DvME1Oq9MZaFyfJeZ80OGfhguy73Y5jLN3ocIbVF/Mnw3+g57ecdpunbrgHk/RZuqJyP4gbJoHWF2i3Lin3f4XoQVetEfTGcxkP7zcfSvL9M1boM15vcVkdRgx5ZZHLE5F5BIGMFJzYM7dy9V9QSwMEFAAAAAgAtjVQXeWzh9EzCAAA/hoAACkAAAB0ZXN0cy90ZXN0X2EyNF9nbG9iYWxfbWFya2V0X21pZ3JhdGlvbi5web1ZW1PjOBZ+71/hmhcn1cIk6dl9gMoD3cl0ZwcCG0JvdwVKJdsK0WBLbkkGMlPz3/dIshKbJBCY2X0hsi7nHH3nLlheCKmDRBRLlKh7xAT6TQmONM2LOcsoKjnTmir9bi5FHhRELzIWB8wdu4BPt+C3RblI7vwy7E7W6/dUKpJhszIXGRN+120mYpjPibyjGufsVhLNBMek93NAVJC/SzKiVHDmF1orXlP484ko2j56F6R0Hiiqr4qWotnczARmEOm86PvLwAHDksjlgEmaaCGXrfax3UbS9FNGCS/deXMsStxEtUMKofvmwusNnOS0HUmqRHZPPSUlSpnQ/urMYR5dnl9NPg3ry1FBJOWA1l3KZMt9qP5UlrTtrvIgmaaWE5LkoR+HAAHVKCWaokKyhGJaSiT0gsprec2H0y+o1+n986DbOeh0YdjpRJ1up4PuKC3MhrB9VGdvyeN4CTC2gH77WFJdSh7A2PGXJV+rYg0p3LXMdD+P3JqT0F6zfZwTzuagEQTQCpkq2CUpSXFc8jSr7USOyCx0C5il4c1aALuGntJyQhml44zekmSJVTmfs0fMKZgVZnwOxmUgqYkKsFmeDkrgUKMqHlSlocY9vTEA1lIPf5Qka9VRc9exoLWRha22faTGgtOWIT3r3MzCnBJVwnVCGFuNmcGPUgDuSSlB4cnS3HuD4fME7klWwgCFKxWHz9FQmuhSmf0Xk+HlcPJ1OMBXYxien5rh+HyKz84Hw1M8GZ4MvoftGs4G2CUWkt0yDu6Z0CzDhKeYPpJEOxRwAeJReU/TnbDvMFwOMOywW/RTxjgNAMtrbkf6Qfy0a29aFhlLiCNmxA/epuWMcgtaG/W2rM4eAUlrAtjiD4AGcyGDx4CBxcKxG5Qbj1bUOtOsu02vrUZEmJ5Phoey4QOHoQc7gkgctjfNra6dR3NxpsEBSi1N+KSaAMgEG49XmMiYaRPpVsb2JC7uUg9iXGlZ5hCQQCqYE/cspXI1MJNNK0YwzTXT4JMOI0nn1/xbXVfdXvQzWol05O+JLjx1a1ToXxffETUTPKFGneCy+DVafJ3voRD4Pes9/mLmdAMWc3jzOk1av5BM1cIBbGWc8VtMSr2AE79TE/ZqGk0p5DlJU+zkTAX4F7gJOJ7UbL70cS8RWZnzPZVpfe1/o1A0QheoQB8np8guw+Xxvtp6W6isYZUzpQyWK6P3XuBuLWkOYCtc8io3p/saf5PpZsxBV5eD//NdJS0oAdUpUJQpX7RRpA+8qsquVZjYdkvnRXi7oDGFOEb7f4CFtIr2UdGIOTbGFSbGvRi72hGwkqaWaf95LHu7GW46W6+epYbfRpfT0fgzPht9npxMR+dj/HU4Gf0yGg62eaoTH/2t4texTxaE34JLVn6QAHmT9jh9wKaaNVXqAwN3LiEgS2JNEjRzz0T5Bl0U/VdmCK+95rWPX4wI1/zj9NParHvoH5BKOy7g7qe6sfDaa8iHjDIbVd0ujTVFrkMew/QDS/XCRJ1SAdoe4UxYgMGTXlltbLhxF/INhIuqYjD0g5qgE8KA7YTe0sdWHq3ajqGUQqLwP6PB9AtU09tKYK/sN9WPLl9smmo7oo9M6ScwrQofvACipvh1cO0R6exwFc87XYPItzdhcTUe/ftqiL9A7TicXO4EZe1OQsqy0NT3BF5mm+cgzhHoyrZf4K87TmzipT2hItPhZuFx0WiDmib5Pg5vIcOTW/oGXEbj6fDzZDT9vpedmK7vCfeI8lQZnq2aGI2kQB6gxEsW0FR7VE0wes4G/ubY8xx48FFkJDF2Z6r0EMXhB/Pb/qtQ7ugnm0GnXieIlGZYcVKoBZhYDmnGVFgL8Cfo/aE+0KJMFjsBM68dqj9bQ/O4LvtnoWtV1WFG7GOEMaoQhaYcOYxNsXdouUcxW03TgimYU4eVIJUhVqteTHVYyedI3tyAWKtUZkWCRLfz/QDZaIHFnXtNeKKneKXFg/C9zZqAKVzA2JEWNRM1JpiArDbqBL5MKHamWCvXn8f75Xyftl8iV1clFz4LmxHAU6XjxvPEBqdt3levN9zLjO2DbYM8nm4r4vcNylZGCeBLbCJtVT5sLwX2SlUf0IfN5OVmIE8e2LO919Wj6462FhKtuJtN7SxcSxKi9UcXPjz/rVm+1jADpS2ETSn94eZp3jfPC760t5DUXhhsjpizDOq0vct5h+g3lKIxGbvBQdf9vhW0reU7h+4Kxtjb1SaOo/HXk9PRIES10dno8hJK3WbE8pWmtRzI8tJgAXThg8RgW+tyKBF5zvSOyOW93D5Y1nzsOCFZpvod2G9f+WDBFM7wGXAIRQKWA7vFzLB5UPT7tQLG7nPr7/td+wF7HMl+76h6wovDqmwOzY5q0gsE3HwOsK/DkYh/o4luGTlRuBY0RGbsJHtdxqhc+tOXk/Fn0zXskYGdl8+K5zqGWotggYmgIbNfTfUt84zxu1rj3MzH9sG2lmtDO+Eyqhs2o/Xaoq3ZWqutV5SeH8Rue/ylBPvVPF95oL6fnY7Gv75ctjF+TzK2KtpMbN682euU9PFqPDgd4tHgmbQeRtGhvVTzWTIv9BJrEmf10ldDvn1lWAjf+iJstqLZtrDnqc1C90pjUszMsXdJnsLPSoSm40Pu4FQ/CHlnhqvXIkglIJBmOcWmIEwW2x2+4VMtiL3JHdVR9ZMIzsHHQqRYCpznc/jon1i5vUZaYcUcajTkiZRxIQUEYRVdiILy589XW+H80bOvdts8Dwq45iXp0+ZxtW8FjKQ/SsBt986EQESDFinDRRnbXsn+U6nx+vZfUEsDBBQAAAAIALY1UF1u/LiU3wIAAMsGAAASAAAAcnVuX3JlZ3Jlc3Npb25zLnB5lVTJbtswEL3rK9STJcRQoyTNBviYtEWLOLBzKQxDoMixPTFFKlzcuF/fobzKTrpcxEXvzbxZOFjV2rjYLm3XK3QOrIsmRldxzdxMYhnjCvBIx2jQ7z/1wi4piglKKIo0M2C1XECSZjUzoFxEprJAHt2ejnsj60wSaGl3s/vYCU5sJx1HBHNglO2Nori5LUjDAoxlsjBeOayg4JoEWHSoVWHO8vPrS7nMc5Fn9bLTPabp0oJZsAZeGhRT2GPxd0jAtdIV8kIAR7vv6eYdhoF9GixQgOJw6PGG/c0hBDjzbqYNuuWOOG8RmWC1I+6eBYu/UE3fosoWlbMa3ZtambVQlXLDxOc3eQYkW7l2KHd+cNYWeHZRTDVJUyB2rlA5mJqmFi106ZfFRBvgjA4yGJ9pPQ+Wry9bwNpoWwNv/LdI1tGuIVz8GyFAz/4I1d5Rq0FRMedXmguQOMVyG3Z+enEUNPcmNH0BNVotIKSN6NDg9nMjdUnJrA0I5I3tUARHht9BbtSYkExOEnZZ3GHhtZbI0ZFmMwfKKypBTWEPYBOvBJVlJZVTKGCBGT47gG2uixevHbUHf/G4encHwLUbIiwQfhIcPBxA1lGsdVW41wXjyHp00NtMm+yJPsNwlaQR1SteD4UY1WZrbxtKxoQIYJtsuQImzEsXbr9rJsBkAi0PjZgcjZvu2lpvvaYrd4pVEHyN1m1x/qm63AjfvpUpc7AtU4BcUaWVVsh3UVKhnGF8/VrBtPA3RyYtrZy1UXneasst9ll7o5jsjP8jEZKWBnRP0/yBgkw6pWGoMlho6ZtqdE5C8JQHs1+N18bKwCtFWaRMlmH6Lns5jXqvkkZAGuEkNlmTWALGH3rx+VUeh2xqRz9+Mjv0nIO1Ey+TNPwwmZ1jXYNYHah1KUgQ9wwlvRd7S9IsxMOldVDdvaJL8jSqDU2QpPP44+lL/6EY3H0e3A2HX2nb/9brnIQC7zRQFL8BUEsDBBQAAAAIALY1UF0FEZc+BAsAAIEYAAATAAAAUEFUQ0hfTUFOSUZFU1QuanNvbpWY23JbuRFF3+crpvScinG/5GdUDaBhM0ORCkk5maTm37MgkZTkUHKmymXLlHQa6Mveq89/fvn117u52erx7m+//of/8N+n3ea7Ho6yvX/cH05zv93sv3zd7hsfPMjhNz3dP2y+HuS02e/uxYW/Pv5+/V1+u+ncH5RPdk/b7V8un8o86YEP76xrxYYRg++5ZZ/jaNbZHnu3NTc1VVKxNgVXe+5zxBZD1zbEpyySY7h7fuIfLw++O+332+OXl+Po/ftD/umjOWlGa+6+WEkzm5p0cq6SQgg21pRrs92awTmLmRpkOtdmMKLGexvtD0fT4+n4Zf29TnL/QQL/3AmnWKsiNs5pYhqFXI3mPR/N4Iu27kJpZYgzGoN6tT5WaUXzDDaEfkneL+dTPp/xvslRt5vd2w744ez96XDQ3eleHzfH/dD7Lo+np4O+nP3ORO0tEnU2Wx2JWX8oah8u+BqiseJbVxeTqS2p98n6XqPWrqUmqXefJuzxoGPTn3ttMzjE5vT7Oe7sQlcYG+xMhsLNFmy1ts4aph3NTC4/XXPd0z8xUzv1Nml3s5bqvLsR9/GwPz4q0b7rfXv6/X4VowvfODhb3Dku/Sim5R5G0ByduGKy9bXYmWvqtfQZqjjhGM6FmmyXXpvhKMOk3NytuDLI6Ar6OnrHzb83u6/38nT6tj9w6XUEX9L297q93N+4knpwjQS7YZsx9MYMzkZPXxhpaXrJyZdQcu+hRjpAvJm9N5lz+s/zvn869f2D3pOA/a5vtps37XoXpjaXu5hQ0rTGc/WRrave58Ec16E6BuVJySU3G9e2RRq94NuKby+h20E2uy/6fb99Wk8/F8HHh3QZFP2+qt6ZbQb8HL3kxmOGrd2oTaPKNJIZU1uljpE73zTc0ehwUboZo0wfKk0SRqcdrgW4pXP6r8ftpm9Ol/htsxvU4fiqJneZMGpd4F7RFe/iCFlN7NG0YUqh+KX4NMIw01o/po0m1FZdCcmGOPNn4bvs9rtN57PDE73+nH8Z9w9M3aXsZLIEE4LrRadm6m/nmM2ZEkK12pDOOIoxTKOV0Fya3dMH0YXW+2jjs/Cvn13C0wOP++Pmbe1ritq8IUQbxU2fGHdk21TjVt8ZpTqtTaOFgM540/lWma1Pp2OGn9be2ndzeO2Av++fDju5pCEKDlInufcuhDJKGKherclrzhLNnNQ9t+RJ/qzS0fIcPGJgkiuzXKtwdpCXahN3RTvcKjsiX2Nl8FOTUKr4Qk6nX27hCnGqlTpN9iPOFJPN5L7Pnj23t17itevI9j+eNrtv++tzmVQTomOaU2Ze7MhzMrfViXdTUPAeNI0+kRxE3udihjblZqS1fjhL7w1nHoRqvt4m1V7mFHy4tIxORJN7RamyZ3ZqLrRyzmV0lLxE71RNZ4a4rUgss46fVrH+zwQf+bfL4XyA9RzKRrWK93ENqWkS1VUsLk47y4yUjuiVhLTcQkgF43NWjCxFv6Fer927b0c9fH8hlHbYjK96lU9r+8W3qE2JPaWuEUfwUstMlBC5dm5Eq6olj2Qblt9QMg1oTTUhM2gBqf8oBdx+fi6fGd+rjQEtzDKz2SnCaJGvTW4+jCTFuBlTnlFVPLnpI9BlM4Af3clnI7zZHfHIpxc4633PHB8vF6ZlSvOuZKep0UZlDDeUSYZ6RCO0Y4qzSRAN2MxY6CfaULrYNku4lXJIYHMi/rrl/mHTX6stx6M+tO3FtzZ/Px8Cn7BOuoyloKn74QGuNMks6hVxdNwi5eHDpBhdMuZFyQr04EYpWT/Jur7Tjc3x+CSc5BLXhZxdnTa7xqN6a04MtV4Jb1JGWPOqmlMfmmxyLQ+nHU+tTPns4cbl3xHCdsX8tt//9swK6Rx13RQZVpO5DABSfeiGLl5Jz265ZVWppk+PMeWcogEoPPk2lL1n98ltv10w7Fm1dPfmrnisaWoHnCJmTEHvnDpcE5g2sBLT5hEVj4NOVe/qEFo+OYAX3i7m/yCjS38/CEd4GTQg8uum0eovsGLNRWtmGcBZma7yeB2MXc2xZeFnBkyifZ0UlnZZE6CChxSHqgbULqOmP6eFfP/qm2fVoR9PB+lntNLDtR4VEgJRYrA+t1izxaKSNUk80m2kcsIYprMuI4UglnS8ddKduGz/dPIet7LbLWZrTwjO6f542l8ZGQqBx8EfTGhpXDKRdKSqIY4sXJ/qeNtinChLDaBVt/T9oB3twppP1e6GV7+Ru2HPZwA9qbZhsQJMHQ4WlkEGEI2+gBA9IKMsOjBFd3GaUZroQHNB98GwfK463znTw1oSVhre3T1yhBCEJ7oWWsm+uIq2DLat4pC+EhAXq5Sbi2bDjwwYXQZ9EDJ8/2c4/Tnu8wS+2rZbZoKw5kyzQUmeHcTGzBUBSFKshbUKJ7Imr1UmK6A+ZqEA1PwWrb8m4Cp7ONvm+Dbv9SL12T/vjai6bdy7CXZCJdLqccXEkbkGQkuVyKTSBobRtGPww3TMLc1dkD6fdkPHeTHrzJseVQ7926XUY1aSnVEamfCJViXj4mphY8JbMBbqn3A6FCJ4z+05ZbBL/Vuz+UPZeV3GttIu9UW2qtJO0ULdfsZqU4nEN5gHEg//jhT4RooZhpFFzCateYo5Mm+f2MpBt/KyF52uurLM5Nt1FXPLGKPXOhrK4TuoZ+CVwarDPKeEukMQ2QdjvWc7IGgQCNBhMvopC3+U4jcQBWyiE5AfTL6aJ7MTYOoOmxk5tAQsMFTOshHiN6mbXAS11xSAVbz1J+h20VhYVP/1JmxncrBHosL/1eNkOCO7FjTXfad1YXA4tcGfJiSJIWWaGnftjVH7GT68H+SztlyMhYWrNkiwU8SyrrikwcAxrPbq0LOMpKNxhWmKhnxDWJBVoPhSJPx/u8f/0ttVRVGj5IOiTZqqyADURIFibLNkA8RoiwpaOMdygq8zS9llU4uyisl75p96oprfNkszLu8UElBv+TWeqpihcmbkI9bKHHe1PTGeoawWwkWWUEwLO+U2LIM8avlcp/UmKf0AqFUuZ+Ga650JxpQMAhy7o5oSIdPq2f2rpQLZpNYJz2oLWRXYTYZfC0K4esY/tcnj45eV06sPQrY0Jy1UDSqn2oGdBVyOstnJbJaKTBA9T60mkuhMpmuFEtErnz+Qpa+AyGHH1Fxvudmd9N2rrrspnHOxCFyri44KB+crLB/rTwPDHqzLNdfY16USm6RBkXFFPjO34OSGIOtK6Y2XJ79d3yGIj6WkHGd3xWIFo0LWlkvayTG8SgfLyoK3CJWxcrCrdM0L4Gq8+RKHBHz0+uDSwDRm18nV6yrbejHTsIEZZeIO8E4qKBmdlpWhVjDOFj63TF0EG/t7wfjQBa8seqm29jAgXKGlZ4N9kkdChkaPhEgvCwQ9Gl5A44n5kALgILS17ibU47OxvcriP572J1LeWW7PDPKqWCU1VghievS5BBfdelFDA0oAgOGSvtQDqZrJs6B0+Nc6nxj1MaS83vuHbH8c+4J7jeUiQndr13A4ayQFOYFfCEkYcC+kU6ANH6OLkcsOWZt4rGv9KOODuOeqEv/7Rv9JdH26SlSrCXNZ7zjbjOspebU23NfWOLPkruuPAIDHOjsUyCoGHNtkY2vjB4k6Bzhb0Y2XEjHkYDC2hREs61lCaoF9hWnOdaTsbJ5WYuprixzDNNaa6T2paGj464u4W5W9dcu3bxDQwVh79NV4XWLBqhEqwCjTr5f8LMkYvgCR7HK1sFuj1nTa4AyGsqx30X/88sd/AVBLAQIUAxQAAAAIALY1UF0C+kx8xQkAAPQXAAAyAAAAAAAAAAAAAACAAQAAAAB1bml2ZXJzYWxfcG9ydGZvbGlvL2dsb2JhbF9tYXJrZXRfbWlncmF0aW9uX2EyNC5weVBLAQIUAxQAAAAIALY1UF0KsDGrZQEAAFgCAAAiAAAAAAAAAAAAAACAARUKAAB0b29scy9taWdyYXRlX2dsb2JhbF9tYXJrZXRfYTI0LnB5UEsBAhQDFAAAAAgAtjVQXeWzh9EzCAAA/hoAACkAAAAAAAAAAAAAAIABugsAAHRlc3RzL3Rlc3RfYTI0X2dsb2JhbF9tYXJrZXRfbWlncmF0aW9uLnB5UEsBAhQDFAAAAAgAtjVQXW78uJTfAgAAywYAABIAAAAAAAAAAAAAAIABNBQAAHJ1bl9yZWdyZXNzaW9ucy5weVBLAQIUAxQAAAAIALY1UF0FEZc+BAsAAIEYAAATAAAAAAAAAAAAAACAAUMXAABQQVRDSF9NQU5JRkVTVC5qc29uUEsFBgAAAAAFAAUAiAEAAHgiAAAAAA=="
EXPECTED_PAYLOAD_SHA256 = "70be523f0bde888b73e7f10d2b1ba87de714ee8e36077cbe21684e507e69140d"
raw=base64.b64decode(PAYLOAD,validate=True)
if hashlib.sha256(raw).hexdigest()!=EXPECTED_PAYLOAD_SHA256:
 raise SystemExit('FAIL_CLOSED: integridade do pacote inválida.')
root=Path(sys.argv[1]).expanduser().resolve(strict=True)
if not (root/'universal_portfolio').is_dir():
 raise SystemExit('FAIL_CLOSED: diretório ativo do Porquinho não encontrado.')

def digest_file(path):
 return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None

def target(rel):
 p=root/rel
 if p.is_symlink() or any(a.is_symlink() for a in p.parents if a!=root.parent):
  raise RuntimeError('FAIL_CLOSED: symlink no caminho '+rel)
 if not p.resolve().is_relative_to(root):
  raise RuntimeError('FAIL_CLOSED: caminho fora do projeto')
 if p.exists() and not p.is_file():
  raise RuntimeError('FAIL_CLOSED: alvo não é arquivo '+rel)
 return p

with zipfile.ZipFile(io.BytesIO(raw)) as package:
 metadata=json.loads(package.read('PATCH_MANIFEST.json'))
 entries=metadata['files']
 for rel in entries:target(rel)
 for rel,expected in metadata['test_baselines'].items():
  if digest_file(target(rel))!=expected:
   raise SystemExit('FAIL_CLOSED: teste existente diverge do pacote coletado: '+rel+'; nenhum arquivo alterado.')
 current={rel:digest_file(target(rel)) for rel in entries}
 already=all(current[rel]==spec['after'] for rel,spec in entries.items())
 if not already:
  for rel,spec in entries.items():
   if current[rel]!=spec['before']:
    raise SystemExit('FAIL_CLOSED: arquivo diverge do estado verificado pelo preflight: '+rel+'; nenhum arquivo alterado.')
 files={rel:package.read(rel) for rel in entries}
 for rel,content in files.items():
  if hashlib.sha256(content).hexdigest()!=entries[rel]['after']:
   raise SystemExit('FAIL_CLOSED: hash interno inválido: '+rel)
 with tempfile.TemporaryDirectory(prefix='porquinho_a24_validation_') as tmp:
  stage=Path(tmp)
  # Copy sources only. Do not copy data/results/models/history or start the app.
  for p in [*(root/'universal_portfolio').rglob('*.py'), *(root/'brain').rglob('*.py')]:
   if p.is_symlink() or any(a.is_symlink() for a in p.parents if a!=root.parent):
    raise SystemExit('FAIL_CLOSED: symlink em fontes de dependência.')
   rel=p.relative_to(root);dst=stage/rel;dst.parent.mkdir(parents=True,exist_ok=True)
   shutil.copy2(p,dst)
  for rel in metadata['test_baselines']:
   dst=stage/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(target(rel),dst)
  for rel,content in files.items():
   dst=stage/rel;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(content)
  (stage/'run_regressions.py').write_bytes(package.read('run_regressions.py'))
  print('VALIDATING_IN_TEMPORARY_SOURCE_COPY',flush=True)
  subprocess.run([sys.executable,'-I','-B',str(stage/'run_regressions.py')],cwd=stage,check=True)
 if already:
  print('ALREADY_APPLIED: hashes A24 e regressões confirmados; nenhuma alteração.')
  raise SystemExit(0)
 # Recheck after staging to avoid overwriting changes made during validation.
 for rel in entries:
  if digest_file(target(rel))!=current[rel]:
   raise SystemExit('FAIL_CLOSED: arquivo mudou durante a validação: '+rel)
 backup=root/('.porquinho_a24_migration_backup_'+datetime.now().strftime('%Y%m%d_%H%M%S_%f'))
 backup.mkdir(mode=0o700)
 for rel in entries:
  p=target(rel)
  if p.exists():
   dst=backup/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dst)
   if digest_file(dst)!=current[rel]:
    raise SystemExit('FAIL_CLOSED: backup divergente; código não alterado.')
 (backup/'PATCH_MANIFEST.json').write_text(json.dumps(metadata,indent=2))
 applied=[]
 def replace_bytes(path,content,mode):
  fd,name=tempfile.mkstemp(prefix='.a24_',dir=path.parent)
  try:
   with os.fdopen(fd,'wb') as h:
    h.write(content);h.flush();os.fsync(h.fileno())
   os.chmod(name,mode);os.replace(name,path)
  finally:
   if os.path.exists(name):os.unlink(name)
 try:
  for rel,content in files.items():
   p=target(rel)
   if digest_file(p)!=current[rel]:raise RuntimeError('Arquivo mudou durante aplicação: '+rel)
   mode=stat.S_IMODE(p.stat().st_mode) if p.exists() else 0o600
   replace_bytes(p,content,mode);applied.append(rel)
  for rel,spec in entries.items():
   if digest_file(target(rel))!=spec['after']:raise RuntimeError('Pós-check divergente: '+rel)
 except BaseException:
  for rel in reversed(applied):
   p=target(rel)
   if digest_file(p)!=entries[rel]['after']:
    print('ROLLBACK_REQUIRES_REVIEW: arquivo mudou externamente: '+rel,flush=True);continue
   old=backup/rel
   if old.is_file():replace_bytes(p,old.read_bytes(),stat.S_IMODE(old.stat().st_mode))
   else:p.unlink()
  print('APPLY_FAILED: rollback tentado; backups preservados em '+str(backup),flush=True)
  raise
 (backup/'APPLIED_OK.txt').write_text('A24 lossless global market migration applied; 371 offline Python tests passed in staging.\n')
 print('PATCH_APPLIED_A24_GLOBAL_MARKET_MIGRATION')
 print('BACKUP='+str(backup))
 print('REGRESSION_OK: 371 testes Python; fixtures sintéticas.')
 print('CANONICAL_PROMOTION=BLOCKED_UNTIL_VERIFIED_PRODUCER')
 print('FINANCIAL_OPERATIONS=NONE; SERVICE_RESTARTS=NONE')
 print('O instalador preservou dados, modelos, memória e histórico existentes.')
 print('Nova cópia global com rastreabilidade por linha; dados e unidades não são inferidos.')
 print('Histórico original permanece intacto. Nenhum vínculo criado, modelo treinado ou dado retroativamente certificado.')
 print('Migração versionada da tabela de mercado; o Brain continua usando seus componentes atuais.')
 print('MIGRATING_GLOBAL_MARKET_COPY',flush=True)
 try:
  subprocess.run([sys.executable,'-I','-B','-c',"import sys,json\nfrom pathlib import Path\nroot=Path(sys.argv[1]).resolve(strict=True);sys.path.insert(0,str(root))\nfrom universal_portfolio.global_market_migration_a24 import migrate\ntry:print(json.dumps(migrate(root),ensure_ascii=False,indent=2))\nexcept Exception as exc:print(json.dumps({'status':'MIGRATION_NOT_COMPLETED','error_type':type(exc).__name__,'reason':str(exc) if type(exc).__name__=='MigrationError' else 'INSPECT_LOCAL_SOURCE_AND_STORAGE','source_modified':False,'runtime_switched':False,'canonical_publication_authorized':False},indent=2))\n",str(root)],cwd=root,check=True,timeout=180)
 except subprocess.SubprocessError as exc:
  print('PATCH_APPLIED; MIGRATION_NOT_COMPLETED:'+type(exc).__name__)
A24_PYTHON
