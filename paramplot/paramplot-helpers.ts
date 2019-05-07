namespace gr_paramplot_dashboard {

    export class DataSeries {
        private name: string;
        private scalarData: vz_chart_helpers.ScalarDatum[];

        constructor(name: string, scalarData: vz_chart_helpers.ScalarDatum[]) {
            this.name = name;
            this.scalarData = scalarData;
        }

        getName(): string {
            return this.name;
        }
        
        setData(scalarData: vz_chart_helpers.ScalarDatum[]) {
            this.scalarData = scalarData;
        }

        getData(){
            return this.scalarData;
        }
    }

}