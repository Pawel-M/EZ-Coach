using System.Collections.Generic;
using EZCoach.Value;
using UnityEngine;

namespace EZCoach.Pong {
    public class ViewStateProvider : AStateProvider {
        [SerializeField] private List<RenderTexture> renderTextures;

        private Texture2D texture2D;
        private int[][] viewStates;

        private void Start() {
            var firstRenderTexture = renderTextures[0];
            var width = firstRenderTexture.width;
            var height = firstRenderTexture.height;
            texture2D = new Texture2D(width, height);

            var numTextures = renderTextures.Count;
            viewStates = new int[numTextures][];
            for (int i = 0; i < numTextures; i++) {
                viewStates[i] = new int[width * height * 3];
            }
        }

        public override object GetStatesDefinition() {
            var firstPlayerRenderTexture = renderTextures[0];
            var width = firstPlayerRenderTexture.width;
            var height = firstPlayerRenderTexture.height;
            return new PixelList(width, height, 3, ChannelRange.BIT8);
        }

        public override List<object> GetStates(int numPlayers) {
            var states = new List<object>(numPlayers);
            for (int i = 0; i < numPlayers; i++) {
                var viewState = viewStates[i];
                UpdateViewState(viewState, renderTextures[i]);
                states.Add(viewState);
            }

            return states;
        }

        private void UpdateViewState(int[] viewState, RenderTexture renderTexture) {
            RenderTexture.active = renderTexture;
            texture2D.ReadPixels(new Rect(0, 0, renderTexture.width, renderTexture.height), 0, 0);
            var pixels = texture2D.GetPixels32();
            for (int i = 0; i < pixels.Length; i++) {
                var index = i * 3;
                var pixel = pixels[i];
                viewState[index] = pixel.r;
                viewState[index + 1] = pixel.g;
                viewState[index + 2] = pixel.b;
            }
        }
    }
}