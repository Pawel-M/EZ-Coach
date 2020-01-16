using System.Collections.Generic;
using UnityEngine;

namespace EZCoach {
    public interface ICommunicationHandler {
        void HandleConnect();
        void HandleStart(int numPlayers, Dictionary<string, object> options = null);
        void HandleActions(object[] actions);
        void HandleStop();
    }
}