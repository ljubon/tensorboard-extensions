import {LitElement, html, property,  customElement} from 'lit-element';
import Dygraph from 'dygraphs';
import 'dygraphs/dist/dygraph.css';

namespace lib {

    export interface DataPoint {
        x: number;
        y: number;
    }

    @customElement('simple-chart')
    export class SimpleChart extends LitElement {

        // data is in the form of a csv string where the first column is the
        @property()
        public data: DataPoint[];

        @property()
        public xAxisLabel: string;

        @property()
        public yAxisLabel: string;

        @property()
        public name: string;

        private readonly chartId: string;
        private graph: Dygraph;

        constructor(){
            super();
            this.chartId = `${this.name}-chart`;
        }

        render(){
            return html`<canvas id="${this.chartId}"></canvas>`
        }

        firstUpdated(_changedProperties): void {
            // create the graph and initialise it with data after the element has been rendered
            let csvData = `${this.xAxisLabel},${this.yAxisLabel}\n`;
            for(let dataPoint of this.data){
                csvData += `${dataPoint.x},${dataPoint.y}\n`;
            }
            this.graph = new Dygraph(document.getElementById(this.chartId), csvData);
        }
    }
}