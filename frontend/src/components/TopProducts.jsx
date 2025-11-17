import { Package, Award } from 'lucide-react';

const TopProducts = ({ data }) => {
  return (
    <div
      className="bg-white rounded-2xl p-6 lg:p-8 border border-slate-200 shadow-lg"
      style={{
        boxShadow: "0 8px 32px rgba(8, 145, 178, 0.12)"
      }}
      data-testid="top-products"
    >
      <div className="flex items-center gap-3 mb-6">
        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg">
          <Package className="w-6 h-6 text-white" />
        </div>
        <div>
          <h3 className="text-lg font-bold text-slate-800">En Çok Satılan Ürünler</h3>
          <p className="text-sm text-slate-500">Bu ay</p>
        </div>
      </div>

      <div className="space-y-4">
        {data.map((product, index) => (
          <div
            key={index}
            className="flex items-center justify-between p-4 rounded-xl bg-gradient-to-r from-slate-50 to-slate-100 hover:from-indigo-50 hover:to-purple-50 transition-all duration-300 border border-slate-200"
            data-testid={`product-item-${index}`}
          >
            <div className="flex items-center gap-4">
              {index === 0 && (
                <Award className="w-6 h-6 text-yellow-500" />
              )}
              <div>
                <p className="font-semibold text-slate-800">{product.code}</p>
                <p className="text-sm text-slate-500">{product.name}</p>
              </div>
            </div>
            <div className="text-right">
              <p className="font-bold text-slate-800">{product.sales}</p>
              <p className="text-sm text-slate-500">satış</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TopProducts;
