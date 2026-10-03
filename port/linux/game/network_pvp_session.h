#ifndef NETWORK_PVP_SESSION_H
#define NETWORK_PVP_SESSION_H
struct network_game;
boolean network_pvp_host_requested(void);
boolean network_pvp_host_settings(struct network_game *game);
void network_pvp_session_update(boolean menu_loaded, real seconds);
void network_pvp_session_end(void);
#endif
