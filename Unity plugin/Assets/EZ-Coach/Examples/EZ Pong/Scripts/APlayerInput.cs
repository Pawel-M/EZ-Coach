using UnityEngine;

namespace EZCoach.Pong {
    public abstract class APlayerInput : MonoBehaviour {

        protected Player player;

        public virtual void Initialize(Player player) {
            this.player = player;
        }

        public abstract PlayerDirection Direction { get; }

        public abstract void Clear();
    }
}