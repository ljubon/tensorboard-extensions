namespace gr_paramplot_dashboard {

    const formatValueOrNaN = (x) => isNaN(x) ? 'NaN' : vz_chart_helpers.multiscaleFormatter(vz_chart_helpers.Y_TOOLTIP_FORMATTER_PRECISION)(x);

    export class DataSeries {
        constructor(private name: string, private scalarData: vz_chart_helpers.ScalarDatum[]) {
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

    export const paramplot_tooltip_columns = (parameter: string, tag: string) => [
        {
            title: 'Series Key',
            evaluate: (d: vz_chart_helpers.Point) => d.dataset.metadata().name, 
        },
        {
            title: tag,
            evaluate: (d: vz_chart_helpers.Point) => formatValueOrNaN(d.datum.scalar),
        },
        {
            title: parameter,
            evaluate: (d: vz_chart_helpers.Point) => vz_chart_helpers.stepFormatter(d.datum.step),
        }
    ];

    export const PARAMPLOT_TOOLTIP_POSITION = vz_chart_helper.TooltipPosition.AUTO;
}