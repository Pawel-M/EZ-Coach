using System.Collections.Generic;
using UnityEngine;

namespace EZCoach.Pong {
    public abstract class AStateProvider : MonoBehaviour {
        public abstract object GetStatesDefinition();
        public abstract List<object> GetStates(int numPlayers);
    }
}