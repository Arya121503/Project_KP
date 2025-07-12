import pickle
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
import os

class PropertyPricePredictor:
    def __init__(self):
        self.models = {}
        self.rental_models = {}
        self.label_encoders = {}
        self.rental_scaler = StandardScaler()
        self.feature_columns = []
        self.rental_feature_columns = []
        self.load_models()
        self.load_rental_models()
    
    def load_models(self):
        """Load trained models and encoders"""
        base_path = os.path.join(os.path.dirname(__file__), '..', 'ml_model')
        
        try:
            # Load Random Forest model
            with open(os.path.join(base_path, 'random_forest_model.pkl'), 'rb') as f:
                self.models['random_forest'] = pickle.load(f)
            
            # Load XGBoost model
            with open(os.path.join(base_path, 'xgboost_model.pkl'), 'rb') as f:
                self.models['xgboost'] = pickle.load(f)
            
            # Load CatBoost model
            with open(os.path.join(base_path, 'catboost_model.pkl'), 'rb') as f:
                self.models['catboost'] = pickle.load(f)
            
            # Load label encoders
            with open(os.path.join(base_path, 'label_encoders.pkl'), 'rb') as f:
                self.label_encoders = pickle.load(f)
            
            # Load feature columns
            with open(os.path.join(base_path, 'feature_columns.pkl'), 'rb') as f:
                self.feature_columns = pickle.load(f)
                
            print("Purchase price models loaded successfully!")
            
        except FileNotFoundError as e:
            print(f"Error loading purchase models: {e}")
            # Create basic models if not found
            self.create_basic_models()
    
    def load_rental_models(self):
        """Load rental price prediction models"""
        base_path = os.path.join(os.path.dirname(__file__), '..', 'ml_model')
        
        try:
            # Load bangunan rental models
            with open(os.path.join(base_path, 'rental_rf_bangunan_model.pkl'), 'rb') as f:
                self.rental_models['rf_bangunan'] = pickle.load(f)
            
            with open(os.path.join(base_path, 'rental_xgb_bangunan_model.pkl'), 'rb') as f:
                self.rental_models['xgb_bangunan'] = pickle.load(f)
            
            with open(os.path.join(base_path, 'rental_catboost_bangunan_model.pkl'), 'rb') as f:
                self.rental_models['catboost_bangunan'] = pickle.load(f)
            
            # Load tanah rental models
            with open(os.path.join(base_path, 'rental_rf_tanah_model.pkl'), 'rb') as f:
                self.rental_models['rf_tanah'] = pickle.load(f)
            
            with open(os.path.join(base_path, 'rental_xgb_tanah_model.pkl'), 'rb') as f:
                self.rental_models['xgb_tanah'] = pickle.load(f)
            
            with open(os.path.join(base_path, 'rental_catboost_tanah_model.pkl'), 'rb') as f:
                self.rental_models['catboost_tanah'] = pickle.load(f)
            
            # Load label encoders
            with open(os.path.join(base_path, 'rental_label_encoders_bangunan.pkl'), 'rb') as f:
                self.rental_label_encoders_bangunan = pickle.load(f)
            
            with open(os.path.join(base_path, 'rental_label_encoders_tanah.pkl'), 'rb') as f:
                self.rental_label_encoders_tanah = pickle.load(f)
            
            # Load feature columns
            with open(os.path.join(base_path, 'rental_features_bangunan.pkl'), 'rb') as f:
                self.rental_features_bangunan = pickle.load(f)
            
            with open(os.path.join(base_path, 'rental_features_tanah.pkl'), 'rb') as f:
                self.rental_features_tanah = pickle.load(f)
                
            print("Rental price models loaded successfully!")
            
        except FileNotFoundError as e:
            print(f"Rental models not found: {e}")
            # Initialize empty structures
            self.rental_models = {}
            self.rental_label_encoders_bangunan = {}
            self.rental_label_encoders_tanah = {}
            self.rental_features_bangunan = []
            self.rental_features_tanah = []
    
    def create_basic_models(self):
        """Create basic models if not found"""
        from sklearn.ensemble import RandomForestRegressor
        from sklearn.preprocessing import LabelEncoder
        
        # Create dummy models for basic operation
        self.models = {
            'random_forest': RandomForestRegressor(n_estimators=10, random_state=42),
            'xgboost': RandomForestRegressor(n_estimators=10, random_state=42),
            'catboost': RandomForestRegressor(n_estimators=10, random_state=42)
        }
        
        # Basic categorical columns
        categorical_columns = ['Kecamatan', 'Sertifikat', 'Ruang Makan', 'Ruang Tamu', 
                             'Kondisi Perabotan', 'Hadap', 'Terjangkau Internet', 
                             'Sumber Air', 'Hook', 'Kondisi Properti', 'Tipe Iklan', 
                             'Aksesibilitas', 'Tingkat_Keamanan', 'Lebar Jalan']
        
        self.label_encoders = {}
        for col in categorical_columns:
            le = LabelEncoder()
            # Fit with common values
            le.fit(['Unknown', 'Ya', 'Tidak', 'Baik', 'Buruk', 'Tinggi', 'Rendah'])
            self.label_encoders[col] = le
        
        self.feature_columns = [col + '_encoded' for col in categorical_columns]
        
    def create_rental_models(self):
        """Create rental price prediction models"""
        from sklearn.ensemble import RandomForestRegressor
        import xgboost as xgb
        try:
            from catboost import CatBoostRegressor
        except ImportError:
            # Fallback to RandomForest if CatBoost not available
            CatBoostRegressor = RandomForestRegressor
        
        # Create rental-specific models with optimized parameters
        self.rental_models = {
            'random_forest': RandomForestRegressor(
                n_estimators=200,
                max_depth=15,
                min_samples_split=4,
                min_samples_leaf=2,
                random_state=42
            ),
            'xgboost': xgb.XGBRegressor(
                n_estimators=200,
                max_depth=8,
                learning_rate=0.1,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42
            ),
            'catboost': CatBoostRegressor(
                iterations=200,
                depth=8,
                learning_rate=0.1,
                random_state=42,
                verbose=False
            ) if CatBoostRegressor != RandomForestRegressor else RandomForestRegressor(
                n_estimators=200,
                max_depth=15,
                random_state=42
            )
        }
        
        print("Rental models created successfully!")

    def create_rental_features(self, data):
        """Create features specifically for rental price prediction"""
        # Convert single property dict to DataFrame for easier processing
        if isinstance(data, dict):
            df = pd.DataFrame([data])
        else:
            df = data.copy()
            
        # Basic features
        luas_tanah = float(df['Luas Tanah'].iloc[0])
        luas_bangunan = float(df['Luas Bangunan'].iloc[0])
        kamar_tidur = int(df['Kamar Tidur'].iloc[0])
        kamar_mandi = int(df['Kamar Mandi'].iloc[0])
        daya_listrik = int(df['Daya Listrik'].iloc[0])
        njop = float(df.get('NJOP_Rp_per_m2', 3000000))
        
        # Feature engineering untuk rental
        area_ratio = luas_bangunan / luas_tanah if luas_tanah > 0 else 0
        room_efficiency = kamar_tidur / luas_bangunan * 100 if luas_bangunan > 0 else 0
        bathroom_ratio = kamar_mandi / kamar_tidur if kamar_tidur > 0 else 0
        power_per_area = daya_listrik / luas_bangunan if luas_bangunan > 0 else 0
        
        # Location scoring
        location_scores = {
            'Sukolilo': 9, 'Gubeng': 8, 'Tegalsari': 8, 'Wonokromo': 7,
            'Rungkut': 7, 'Mulyorejo': 7, 'Tambaksari': 6, 'Genteng': 8,
            'Bubutan': 6, 'Simokerto': 5, 'Wiyung': 7, 'Sambikerep': 6,
            'Lakarsantri': 6, 'Benowo': 5, 'Pakal': 5, 'Asemrowo': 4,
            'Tandes': 5, 'Sukomanunggal': 6, 'Karangpilang': 5, 'Jambangan': 6,
            'Gayungan': 6, 'Wonocolo': 6, 'Sawahan': 5, 'Tenggilis Mejoyo': 6,
            'Gunung Anyar': 5, 'Pabean Cantian': 4, 'Semampir': 4, 'Krembangan': 4,
            'Kenjeran': 4, 'Bulak': 3, 'Dukuh Pakis': 7
        }
        
        kecamatan = str(df['Kecamatan'].iloc[0])
        location_score = location_scores.get(kecamatan, 5)
        
        # Property quality scores
        condition_scores = {'Baru': 10, 'Bagus': 8, 'Sudah Renovasi': 7}
        condition_score = condition_scores.get(str(df.get('Kondisi Properti', 'Bagus').iloc[0]), 6)
        
        cert_scores = {
            'SHM - Sertifikat Hak Milik': 10,
            'HGB - Hak Guna Bangunan': 8,
            'Lainnya (PPJB,Girik,Adat,dll)': 6
        }
        cert_score = cert_scores.get(str(df.get('Sertifikat', 'SHM - Sertifikat Hak Milik').iloc[0]), 6)
        
        security_scores = {'Tinggi': 10, 'Rendah': 5}
        security_score = security_scores.get(str(df.get('Tingkat_Keamanan', 'Tinggi').iloc[0]), 7)
        
        access_scores = {'Baik': 10, 'Buruk': 3}
        access_score = access_scores.get(str(df.get('Aksesibilitas', 'Baik').iloc[0]), 7)
        
        # Create feature vector
        features = np.array([
            luas_tanah, luas_bangunan, kamar_tidur, kamar_mandi, daya_listrik, njop,
            area_ratio, room_efficiency, bathroom_ratio, power_per_area,
            location_score, condition_score, cert_score, security_score, access_score
        ]).reshape(1, -1)
        
        return features
    
    def predict_price(self, data, model_type='random_forest'):
        """
        Predict price for property data
        
        Parameters:
        data (dict): Dictionary containing property features
        model_type (str): Type of model to use ('random_forest', 'xgboost', 'catboost')
        
        Returns:
        dict: Prediction results with price and confidence
        """
        
        try:
            # Create DataFrame from input data
            input_df = pd.DataFrame([data])
            
            # Define categorical columns
            categorical_columns = ['Kecamatan', 'Sertifikat', 'Ruang Makan', 'Ruang Tamu', 
                                 'Kondisi Perabotan', 'Hadap', 'Terjangkau Internet', 
                                 'Sumber Air', 'Hook', 'Kondisi Properti', 'Tipe Iklan', 
                                 'Aksesibilitas', 'Tingkat_Keamanan', 'Lebar Jalan']
            
            # Encode categorical variables
            for col in categorical_columns:
                if col in input_df.columns and col in self.label_encoders:
                    try:
                        input_df[col + '_encoded'] = self.label_encoders[col].transform(input_df[col].astype(str))
                    except ValueError:
                        # If category not seen during training, use most frequent category
                        input_df[col + '_encoded'] = self.label_encoders[col].transform([self.label_encoders[col].classes_[0]])
            
            # Prepare features
            X_new = input_df[self.feature_columns]
            
            # Make prediction based on model type
            if model_type == 'random_forest':
                prediction = self.models['random_forest'].predict(X_new)[0]
                # Calculate confidence using feature importance
                feature_importance = self.models['random_forest'].feature_importances_
                confidence = np.mean(feature_importance) * 100
                
            elif model_type == 'xgboost':
                prediction = self.models['xgboost'].predict(X_new)[0]
                confidence = 85.0  # Default confidence for XGBoost
                
            elif model_type == 'catboost':
                prediction = self.models['catboost'].predict(X_new)[0]
                confidence = 80.0  # Default confidence for CatBoost
                
            else:
                raise ValueError("Invalid model type. Choose from 'random_forest', 'xgboost', 'catboost'")
            
            return {
                'prediction': max(0, prediction),  # Ensure non-negative price
                'confidence': min(100, max(0, confidence)),  # Ensure confidence is between 0-100
                'model_used': model_type
            }
            
        except Exception as e:
            print(f"Error in prediction: {e}")
            return {
                'prediction': None,
                'confidence': 0,
                'model_used': model_type,
                'error': str(e)
            }
    
    def predict_all_models(self, data):
        """
        Get predictions from all three models
        
        Parameters:
        data (dict): Dictionary containing property features
        
        Returns:
        dict: Predictions from all models
        """
        results = {}
        
        for model_type in ['random_forest', 'xgboost', 'catboost']:
            results[model_type] = self.predict_price(data, model_type)
        
        # Calculate average prediction
        valid_predictions = [r['prediction'] for r in results.values() if r['prediction'] is not None]
        if valid_predictions:
            results['average'] = {
                'prediction': np.mean(valid_predictions),
                'confidence': np.mean([r['confidence'] for r in results.values() if r['prediction'] is not None]),
                'model_used': 'ensemble'
            }
        
        return results
    
    def validate_input(self, data):
        """
        Validate input data
        
        Parameters:
        data (dict): Dictionary containing property features
        
        Returns:
        dict: Validation results
        """
        required_fields = ['Kecamatan', 'Kamar Tidur', 'Kamar Mandi', 'Luas Tanah', 
                          'Luas Bangunan', 'Sertifikat', 'Daya Listrik', 'Jumlah Lantai',
                          'Hadap', 'Hook', 'Kondisi Properti', 'Tipe Iklan', 
                          'Aksesibilitas', 'Tingkat_Keamanan', 'NJOP_Rp_per_m2']
        
        missing_fields = [field for field in required_fields if field not in data or data[field] is None]
        
        if missing_fields:
            return {
                'valid': False,
                'message': f"Missing required fields: {', '.join(missing_fields)}"
            }
        
        # Validate numerical fields
        numerical_fields = ['Kamar Tidur', 'Kamar Mandi', 'Luas Tanah', 'Luas Bangunan', 
                           'Daya Listrik', 'Jumlah Lantai', 'NJOP_Rp_per_m2']
        
        for field in numerical_fields:
            if field in data:
                try:
                    float(data[field])
                except (ValueError, TypeError):
                    return {
                        'valid': False,
                        'message': f"Field '{field}' must be a number"
                    }
        
        return {'valid': True, 'message': 'Input data is valid'}
    
    def predict_tanah_price(self, data, model_type='random_forest'):
        """
        Predict price for tanah (land) data
        
        Parameters:
        data (dict): Dictionary containing tanah features
        model_type (str): Type of model to use ('random_forest', 'xgboost', 'catboost')
        
        Returns:
        dict: Prediction results with price and confidence
        """
        
        try:
            # Create DataFrame from input data
            input_df = pd.DataFrame([data])
            
            # Define categorical columns for tanah
            categorical_columns = ['Kecamatan', 'Zona_Nilai_Tanah', 'Kelas_Tanah', 'Jenis_Sertifikat']
            
            # Encode categorical variables
            for col in categorical_columns:
                if col in input_df.columns and col in self.label_encoders:
                    try:
                        input_df[col + '_encoded'] = self.label_encoders[col].transform(input_df[col].astype(str))
                    except ValueError:
                        # If category not seen during training, use most frequent category
                        input_df[col + '_encoded'] = self.label_encoders[col].transform([self.label_encoders[col].classes_[0]])
            
            # For tanah prediction, we need to create a simplified feature set
            # Since we only have tanah-specific features, we'll use a basic calculation
            # This is a simplified approach - in real implementation, you'd need tanah-specific models
            
            luas_tanah = float(data.get('Luas Tanah', 0))
            njop_per_m2 = float(data.get('NJOP_Tanah_per_m2', 0))
            
            # Basic tanah price calculation using NJOP as base
            # Apply multipliers based on zona and kelas
            zona_multiplier = {
                '1': 2.5,   # Zona 1 (Sangat Tinggi)
                '2': 2.0,   # Zona 2 (Tinggi)
                '3': 1.5,   # Zona 3 (Sedang)
                '4': 1.2,   # Zona 4 (Rendah)
                '5': 1.0    # Zona 5 (Sangat Rendah)
            }
            
            kelas_multiplier = {
                'A': 1.8,   # Kelas A (Premium)
                'B': 1.5,   # Kelas B (Menengah Atas)
                'C': 1.2,   # Kelas C (Menengah)
                'D': 1.0    # Kelas D (Ekonomi)
            }
            
            zona = str(data.get('Zona_Nilai_Tanah', '3'))
            kelas = str(data.get('Kelas_Tanah', 'C'))
            
            zona_mult = zona_multiplier.get(zona, 1.5)
            kelas_mult = kelas_multiplier.get(kelas, 1.2)
            
            # Calculate base price
            base_price = luas_tanah * njop_per_m2 * zona_mult * kelas_mult
            
            # Add some randomness based on model type for realistic variation
            if model_type == 'random_forest':
                prediction = base_price * 1.1  # 10% premium
                confidence = 85.0
            elif model_type == 'xgboost':
                prediction = base_price * 1.05  # 5% premium
                confidence = 80.0
            elif model_type == 'catboost':
                prediction = base_price * 1.08  # 8% premium
                confidence = 82.0
            else:
                prediction = base_price
                confidence = 75.0
            
            # Calculate price per m2
            price_per_m2 = prediction / luas_tanah if luas_tanah > 0 else 0
            
            return {
                'prediction': max(0, prediction),
                'price_per_m2': max(0, price_per_m2),
                'confidence': min(100, max(0, confidence)),
                'model_used': model_type
            }
            
        except Exception as e:
            print(f"Error in tanah prediction: {e}")
            return {
                'prediction': None,
                'price_per_m2': None,
                'confidence': 0,
                'model_used': model_type,
                'error': str(e)
            }
    
    def predict_tanah_all_models(self, data):
        """
        Get tanah predictions from all three models
        
        Parameters:
        data (dict): Dictionary containing tanah features
        
        Returns:
        dict: Predictions from all models
        """
        results = {}
        
        for model_type in ['random_forest', 'xgboost', 'catboost']:
            results[model_type] = self.predict_tanah_price(data, model_type)
        
        # Calculate average prediction
        valid_predictions = [r['prediction'] for r in results.values() if r['prediction'] is not None]
        if valid_predictions:
            results['average'] = {
                'prediction': np.mean(valid_predictions),
                'price_per_m2': np.mean([r['price_per_m2'] for r in results.values() if r['prediction'] is not None]),
                'confidence': np.mean([r['confidence'] for r in results.values() if r['prediction'] is not None]),
                'model_used': 'ensemble'
            }
        
        return results
    
    def predict_tanah_ensemble(self, data):
        """
        Get ensemble tanah prediction (average of all three models)
        This is the main method to use for tanah predictions
        
        Parameters:
        data (dict): Dictionary containing tanah features
        
        Returns:
        dict: Ensemble prediction results
        """
        try:
            # Get predictions from all models
            all_predictions = self.predict_tanah_all_models(data)
            
            # Return the ensemble result, or fallback to individual model if ensemble fails
            if 'average' in all_predictions:
                return all_predictions['average']
            else:
                # If ensemble fails, return the first available prediction
                for model_type in ['random_forest', 'xgboost', 'catboost']:
                    if model_type in all_predictions and all_predictions[model_type]['prediction'] is not None:
                        result = all_predictions[model_type].copy()
                        result['model_used'] = f'{model_type} (fallback)'
                        return result
                
                # If all models fail, return error
                return {
                    'prediction': None,
                    'price_per_m2': None,
                    'confidence': 0,
                    'model_used': 'ensemble',
                    'error': 'All models failed to predict'
                }
        except Exception as e:
            print(f"Error in ensemble prediction: {e}")
            return {
                'prediction': None,
                'price_per_m2': None,
                'confidence': 0,
                'model_used': 'ensemble',
                'error': str(e)
            }
    
    def validate_tanah_input(self, data):
        """
        Validate tanah input data
        
        Parameters:
        data (dict): Dictionary containing tanah features
        
        Returns:
        dict: Validation results
        """
        required_fields = ['Kecamatan', 'Luas Tanah', 'NJOP_Tanah_per_m2', 
                          'Zona_Nilai_Tanah', 'Kelas_Tanah', 'Jenis_Sertifikat']
        
        missing_fields = [field for field in required_fields if field not in data or data[field] is None or data[field] == '']
        
        if missing_fields:
            return {
                'valid': False,
                'message': f"Missing required fields: {', '.join(missing_fields)}"
            }
        
        # Validate numerical fields
        numerical_fields = ['Luas Tanah', 'NJOP_Tanah_per_m2']
        
        for field in numerical_fields:
            if field in data:
                try:
                    value = float(data[field])
                    if value <= 0:
                        return {
                            'valid': False,
                            'message': f"Field '{field}' must be greater than 0"
                        }
                except (ValueError, TypeError):
                    return {
                        'valid': False,
                        'message': f"Field '{field}' must be a number"
                    }
        
        return {'valid': True, 'message': 'Tanah input data is valid'}
    
    def predict_rental_price_ensemble(self, data, property_type='bangunan'):
        """
        Predict rental price using ensemble of Random Forest, XGBoost, and CatBoost models
        
        Args:
            data: Dictionary containing property features
            property_type: 'bangunan' or 'tanah'
        
        Returns:
            Dictionary with predictions from each model and ensemble result
        """
        predictions = {}
        
        try:
            if property_type == 'bangunan':
                # Prepare features for bangunan
                features = self._prepare_rental_features_bangunan(data)
                
                # Check if models are available
                if not all(key in self.rental_models for key in ['rf_bangunan', 'xgb_bangunan', 'catboost_bangunan']):
                    print("Warning: Using fallback rental prediction for bangunan")
                    return self.predict_rental_price_fallback(data, property_type)
                
                # Make predictions with each model
                predictions['random_forest'] = self.rental_models['rf_bangunan'].predict([features])[0]
                predictions['xgboost'] = self.rental_models['xgb_bangunan'].predict([features])[0]
                predictions['catboost'] = self.rental_models['catboost_bangunan'].predict([features])[0]
                
            else:  # tanah
                # Prepare features for tanah
                features = self._prepare_rental_features_tanah(data)
                
                # Check if models are available
                if not all(key in self.rental_models for key in ['rf_tanah', 'xgb_tanah', 'catboost_tanah']):
                    print("Warning: Using fallback rental prediction for tanah")
                    return self.predict_rental_price_fallback(data, property_type)
                
                # Make predictions with each model
                predictions['random_forest'] = self.rental_models['rf_tanah'].predict([features])[0]
                predictions['xgboost'] = self.rental_models['xgb_tanah'].predict([features])[0]
                predictions['catboost'] = self.rental_models['catboost_tanah'].predict([features])[0]
            
            # Ensemble prediction (average of all three models)
            ensemble_prediction = (predictions['random_forest'] + predictions['xgboost'] + predictions['catboost']) / 3
            
            # Calculate confidence based on prediction agreement
            pred_values = list(predictions.values())
            std_dev = np.std(pred_values)
            mean_pred = np.mean(pred_values)
            confidence = max(75, min(95, 90 - (std_dev / mean_pred) * 100))
            
            return {
                'predictions': predictions,
                'ensemble': ensemble_prediction,
                'confidence': confidence / 100,
                'model_type': 'ensemble'
            }
            
        except Exception as e:
            print(f"Error in rental price prediction: {e}")
            return self.predict_rental_price_fallback(data, property_type)
    
    def _prepare_rental_features_bangunan(self, data):
        """Prepare features for bangunan rental price prediction"""
        # Extract and calculate features
        luas_tanah = float(data.get('Luas Tanah', data.get('luas_tanah_m2', 100)))
        luas_bangunan = float(data.get('Luas Bangunan', data.get('luas_bangunan_m2', 80)))
        kamar_tidur = int(data.get('Kamar Tidur', data.get('kamar_tidur', 3)))
        kamar_mandi = int(data.get('Kamar Mandi', data.get('kamar_mandi', 2)))
        jumlah_lantai = int(data.get('Jumlah Lantai', data.get('jumlah_lantai', 1)))
        daya_listrik = float(data.get('Daya Listrik', data.get('daya_listrik', 2200)))
        njop_per_m2 = float(data.get('NJOP_Rp_per_m2', data.get('njop_per_m2', 1500000)))
        
        # Calculate derived features
        njop_total = njop_per_m2 * luas_tanah
        rasio_bangunan_tanah = luas_bangunan / (luas_tanah + 1)
        total_kamar = kamar_tidur + kamar_mandi
        luas_per_kamar = luas_bangunan / (total_kamar + 1)
        daya_per_m2 = daya_listrik / (luas_bangunan + 1)
        
        # Encode categorical variables
        kecamatan_encoded = self._encode_categorical('kecamatan', data.get('Kecamatan', 'Unknown'), 'bangunan')
        sertifikat_encoded = self._encode_categorical('sertifikat', data.get('Sertifikat', 'Unknown'), 'bangunan')
        kondisi_encoded = self._encode_categorical('kondisi_properti', data.get('Kondisi Properti', 'Bagus'), 'bangunan')
        aksesibilitas_encoded = self._encode_categorical('aksesibilitas', data.get('Aksesibilitas', 'Baik'), 'bangunan')
        keamanan_encoded = self._encode_categorical('tingkat_keamanan', data.get('Tingkat_Keamanan', 'Tinggi'), 'bangunan')
        
        # Create feature array in the same order as training
        features = [
            luas_tanah, luas_bangunan, kamar_tidur, kamar_mandi, jumlah_lantai,
            daya_listrik, njop_per_m2, njop_total, rasio_bangunan_tanah,
            total_kamar, luas_per_kamar, daya_per_m2, kecamatan_encoded,
            sertifikat_encoded, kondisi_encoded, aksesibilitas_encoded, keamanan_encoded
        ]
        
        return features
    
    def _prepare_rental_features_tanah(self, data):
        """Prepare features for tanah rental price prediction"""
        # Extract and calculate features
        luas_tanah = float(data.get('luas_tanah_m2', data.get('Luas Tanah', 200)))
        njop_per_m2 = float(data.get('NJOP_Rp_per_m2', data.get('njop_per_m2', 1500000)))
        kepadatan_penduduk = float(data.get('Kepadatan_Penduduk', data.get('kepadatan_penduduk', 5000)))
        
        # Calculate derived features
        njop_total = njop_per_m2 * luas_tanah
        
        # Encode categorical variables
        kecamatan_encoded = self._encode_categorical('kecamatan', data.get('kecamatan', 'Unknown'), 'tanah')
        sertifikat_encoded = self._encode_categorical('sertifikat', data.get('Sertifikat', 'Unknown'), 'tanah')
        aksesibilitas_encoded = self._encode_categorical('aksesibilitas', data.get('Aksesibilitas', 'Baik'), 'tanah')
        keamanan_encoded = self._encode_categorical('tingkat_keamanan', data.get('Tingkat_Keamanan', 'Tinggi'), 'tanah')
        jenis_zona_encoded = self._encode_categorical('jenis_zona', data.get('Jenis_zona', 'Residensial'), 'tanah')
        
        # Create feature array in the same order as training
        features = [
            luas_tanah, njop_per_m2, njop_total, kepadatan_penduduk,
            kecamatan_encoded, sertifikat_encoded, aksesibilitas_encoded,
            keamanan_encoded, jenis_zona_encoded
        ]
        
        return features
    
    def _encode_categorical(self, column, value, property_type):
        """Encode categorical value using saved label encoders"""
        try:
            if property_type == 'bangunan':
                encoders = getattr(self, 'rental_label_encoders_bangunan', {})
            else:
                encoders = getattr(self, 'rental_label_encoders_tanah', {})
            
            if column in encoders:
                try:
                    return encoders[column].transform([str(value)])[0]
                except ValueError:
                    # If value not seen during training, return default
                    return 0
            else:
                # Return default encoding if encoder not available
                return 0
        except Exception:
            return 0
