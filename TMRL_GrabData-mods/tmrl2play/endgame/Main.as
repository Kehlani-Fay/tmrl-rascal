bool enableSplitscreenCollisions = true;

void RenderMenu()
{
    if(UI::MenuItem("Enable splitscreen collisions")) {
        enableSplitscreenCollisions = true;
    }
    if(UI::MenuItem("Disable splitscreen collisions")) {
        enableSplitscreenCollisions = false;
    }
}

void Update(float dt){
    if(enableSplitscreenCollisions){
        CGameCtnApp@ app = GetApp();   
        CGamePlaygroundScript@ playgroundScript = app.PlaygroundScript;
        CGameServerPlugin@ endgame = CMwNod.CGameServerPlugin;


        if(!(playgroundScript is null)){
            CSmArenaRulesMode@ arenaRules = cast<CSmArenaRulesMode>(playgroundScript);
            if(!(arenaRules is null)){
                arenaRules.UsePvPCollisions = true;
                arenaRules.UsePvECollisions = true;
            }
        }
    }
}