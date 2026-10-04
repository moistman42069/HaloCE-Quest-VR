#ifndef HALO_NETWORK_BROWSER_H
#define HALO_NETWORK_BROWSER_H
struct network_advertised_game;
void network_browser_begin(void);
void network_browser_end(void);
/* Nine stock widget rows: previous/refresh, seven games, next/refresh. */
long network_browser_rows(struct network_advertised_game **rows, short selected, short controller);
/* Resolve only to a currently advertised native record; NULL means navigation,
 * pending discovery or rejection. Never pass a synthetic record to netcode. */
struct network_advertised_game *network_browser_select(struct network_advertised_game *row, short controller);
boolean network_browser_text(long row, wchar_t *text, long capacity);
char const *network_browser_status(void);
#endif
